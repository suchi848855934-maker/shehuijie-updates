import hashlib, json, logging, logging.handlers, os, pathlib, queue, re, shutil, subprocess, sys, tempfile, threading, time, urllib.request, zipfile
ROOT = pathlib.Path(__file__).resolve().parent
STATE = pathlib.Path(os.environ.get('LOCALAPPDATA', str(pathlib.Path.home()))) / 'SheHuiJie'
STATE.mkdir(parents=True, exist_ok=True)
log = logging.getLogger('update'); log.setLevel(logging.INFO)
h = logging.handlers.RotatingFileHandler(STATE/'update.log', maxBytes=1000000, backupCount=3, encoding='utf-8'); log.addHandler(h)
VERSION = json.loads((ROOT/'version.json').read_text(encoding='utf-8'))['version'] if (ROOT/'version.json').exists() else '0.0.0'
REPO = 'suchi848855934-maker/shehuijie-updates'
FILES = {'pet.py', 'launcher.py', 'updater.py', 'version.json', 'README.txt', '启动社会姐.bat'}
def version(s):
    if not re.fullmatch(r'\d+\.\d+\.\d+', s): raise ValueError('版本号无效')
    return tuple(map(int, s.split('.')))
def fetch(url, limit):
    if not url.startswith('https://'): raise ValueError('仅允许 HTTPS')
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent':'SheHuiJie-Updater'}), timeout=30) as r:
        data = r.read(limit+1)
    if len(data)>limit: raise ValueError('下载超过大小限制')
    return data

def unpack(package, target):
    with zipfile.ZipFile(package) as z:
        names = z.namelist()
        if len(names)!=len(set(names)) or set(names)!=FILES: raise ValueError('更新包文件清单不符')
        if sum(i.file_size for i in z.infolist())>20000000: raise ValueError('解压大小超限')
        for i in z.infolist():
            if (i.external_attr >> 16) & 0o170000 == 0o120000: raise ValueError('不允许符号链接')
        z.extractall(target)

def check():
    m = json.loads(fetch(f'https://raw.githubusercontent.com/{REPO}/main/latest.json', 100000))
    if version(m['version'])<=version(VERSION): return None
    expected = f'https://github.com/{REPO}/releases/download/v{m["version"]}/shehuijie.zip'
    if m['url']!=expected or not re.fullmatch('[0-9a-f]{64}', m['sha256']): raise ValueError('更新清单无效')
    data = fetch(expected, 10000000)
    if hashlib.sha256(data).hexdigest()!=m['sha256']: raise ValueError('SHA-256 校验失败')
    path = STATE/'download.zip'; path.write_bytes(data)
    (STATE/'download.sha256').write_text(m['sha256'], encoding='ascii')
    with tempfile.TemporaryDirectory(dir=STATE) as t:
        unpack(path, t)
        if json.loads((pathlib.Path(t)/'version.json').read_text(encoding='utf-8'))['version']!=m['version']: raise ValueError('包版本不符')
    return m

def attach(root):
    from tkinter import messagebox
    q = queue.Queue()
    def worker():
        try: q.put(('ok', check()))
        except Exception: log.exception('检查或下载失败'); q.put(('error', None))
    def poll():
        try: status, m = q.get_nowait()
        except queue.Empty: root.after(250, poll); return
        if status=='ok' and m:
            if messagebox.askyesno('社会姐更新已下载', f'新版本 {m["version"]}\n\n{str(m.get("notes", ""))[:5000]}\n\n已通过 SHA-256 校验。现在安装并重启？', parent=root):
                helper = STATE/'install_helper.py'; shutil.copy2(__file__, helper)
                subprocess.Popen([sys.executable, str(helper), '--install', str(ROOT), str(os.getpid())], cwd=STATE)
                root.destroy()
        elif status=='error': log.info('下次启动重试；当前版本继续运行')
    threading.Thread(target=worker, daemon=True).start(); root.after(250, poll)

def install(target, pid):
    import ctypes
    from ctypes import wintypes
    kernel = ctypes.windll.kernel32
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    kernel.WaitForSingleObject.restype = wintypes.DWORD
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    expected = (STATE/'download.sha256').read_text(encoding='ascii')
    if hashlib.sha256((STATE/'download.zip').read_bytes()).hexdigest() != expected:
        raise ValueError('安装前 SHA-256 复核失败')
    handle = ctypes.windll.kernel32.OpenProcess(0x100000, False, pid)
    if handle:
        try:
            if ctypes.windll.kernel32.WaitForSingleObject(handle, 60000)!=0: raise RuntimeError('旧进程未退出')
        finally: ctypes.windll.kernel32.CloseHandle(handle)
    backup = STATE / ('backup-'+str(time.time_ns())); backup.mkdir()
    touched = []
    with tempfile.TemporaryDirectory(dir=STATE) as stage:
        unpack(STATE/'download.zip', stage)
        try:
            for name in FILES:
                dst=target/name
                if dst.exists(): shutil.copy2(dst, backup/name)
                touched.append(name); shutil.copy2(pathlib.Path(stage)/name, dst)
            token=STATE/('health-'+str(time.time_ns()))
            proc=subprocess.Popen([sys.executable, str(target/'launcher.py'), '--health', str(token)], cwd=target)
            for _ in range(150):
                if token.exists(): log.info('安装成功，备份位于 %s', backup); token.unlink(); return
                if proc.poll() is not None: break
                time.sleep(.2)
            if proc.poll() is None:
                proc.terminate(); proc.wait(timeout=10)
            raise RuntimeError('新版本启动未通过健康检查')
        except Exception:
            log.exception('安装失败，开始回滚')
            for name in touched:
                if (backup/name).exists(): shutil.copy2(backup/name, target/name)
                else: (target/name).unlink(missing_ok=True)
            subprocess.Popen([sys.executable, str(target/'launcher.py')], cwd=target)
            log.info('已恢复旧版本')
if __name__=='__main__' and len(sys.argv)==4 and sys.argv[1]=='--install':
    try: install(pathlib.Path(sys.argv[2]), int(sys.argv[3]))
    except Exception: log.exception('安装器失败')
