"""本机陪伴界面；不上传聊天或偏好。"""
import json, math, os, pathlib, random, sys, time
import tkinter as tk
from tkinter import ttk, messagebox
from pet import SheHuiJie, W, H
import updater
BG, CARD, INK, MUTED, ACCENT = '#F4F3ED', '#FFFFFF', '#253D37', '#687A72', '#2E7662'
FONT = 'Microsoft YaHei UI'

class Mind:
    def __init__(self, data=None, now=None):
        data = data if isinstance(data, dict) else {}
        now = time.time() if now is None else now
        def number(key, default, low, high):
            try:
                n=float(data.get(key,default))
                return min(high,max(low,n)) if math.isfinite(n) else default
            except (ValueError,TypeError): return default
        self.fullness=number('fullness',75,0,100)
        self.bond=number('bond',10,0,100)
        self.last=number('last',now,0,now)
        self.last_feed=0; self.last_pet=0
        self.advance(now)
    def advance(self, now):
        hours=max(0,now-self.last)/3600
        self.fullness=max(0,self.fullness-min(hours,24)*3)
        self.last=now
    def mood(self, hour):
        if self.fullness<25: return '等一份小鱼干'
        if hour>=23 or hour<7: return '困困的，陪你安静一会儿'
        if self.bond>=40: return '见到你就开心'
        return '今天也很有精神'
    def feed(self, now):
        self.advance(now)
        if now-self.last_feed<30: return '慢一点喵，上一口还没吃完。'
        if self.fullness>=95: return '已经吃饱啦，陪我玩一会儿吧。'
        self.last_feed=now; self.fullness=min(100,self.fullness+20); self.bond=min(100,self.bond+1)
        return '小鱼干收到！这份心意本姐记住了。'
    def pet(self, now):
        if now-self.last_pet>=5:
            self.bond=min(100,self.bond+0.5); self.last_pet=now
        return random.choice(['呼噜……再摸一下。','今天的烦恼，分本姐一点。','被你摸摸，心情都变好了。'])
    def reply(self, text, hour):
        if any(w in text for w in ('难过','累','烦','压力','伤心')): return '先歇一小会儿吧。喝口水，把眼前的事拆成小小一步，本姐陪着你。'
        if any(w in text for w in ('饿','吃','鱼')): return '想一起吃点东西！点一下「喂小鱼干」试试。' if self.fullness<75 else '本姐吃得挺满足，你也记得按时吃饭。'
        if any(w in text for w in ('睡','晚安')): return '晚安，把今天先放下。点「休息 / 起床」，本姐也能陪你睡。'
        if any(w in text for w in ('工作','学习','专注')): return '先专心做一件事吧。「专注」页可以陪你计时，结束了我们再摸鱼。'
        if any(w in text for w in ('你好','早','晚上')): return '早上好，新的一天慢慢来。' if 6<=hour<12 else '你回来啦，本姐在这里。'
        return self.mood(hour)+'。本姐会回应问候、心情、吃饭、睡觉和专注这些话题。'
    def data(self): return dict(fullness=self.fullness,bond=self.bond,last=self.last)

class Companion:
    def __init__(self, root):
        self.root=root; self.panel=None; self.deadline=None; self.check_updates=None
        self.running=True; self.last_spoken=time.monotonic(); self.last_action=time.monotonic()
        self.prefs_path=updater.STATE/'preferences.json'
        try: self.prefs=json.loads(self.prefs_path.read_text(encoding='utf-8'))
        except (OSError,ValueError): self.prefs={}
        if not isinstance(self.prefs,dict): self.prefs={}
        self.mind=Mind(self.prefs.get('mind'))
        self.app=SheHuiJie(root)
        self.move=tk.BooleanVar(value=self.prefs.get('move',True) is True)
        self.top=tk.BooleanVar(value=self.prefs.get('top',True) is True)
        self.quiet=tk.BooleanVar(value=self.prefs.get('quiet',False) is True)
        self.smart=tk.BooleanVar(value=self.prefs.get('smart',True) is True)
        self.speed=tk.DoubleVar(value=1.3)
        self.app.roaming=self.move.get()
        self.root.attributes('-topmost',self.top.get())
        try: self.app.x=float(self.prefs.get('x',180)); self.app.y=float(self.prefs.get('y',180))
        except (ValueError,TypeError): self.app.x,self.app.y=180,180
        self.home()
        self.app.canvas.tag_bind('entry','<Button-1>',lambda e:self.open_panel())
        self.app.pet=self.pet; self.app.say_random=lambda: self.say(self.mind.reply('你好',time.localtime().tm_hour))
        self.app.canvas.bind('<Double-Button-1>',lambda e:self.pet())
        self.app.menu.delete(0,'end')
        for label,command in [('打开陪伴面板',self.open_panel),('摸摸头',self.pet),('喂小鱼干',self.feed),('休息 / 起床',self.rest),('回到屏幕内',self.home)]:
            self.app.menu.add_command(label=label,command=command)
        self.app.menu.add_separator(); self.app.menu.add_command(label='退出社会姐',command=self.close)
        self.root.bind('<Escape>',lambda e:self.close())
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.bind('<Destroy>',self.on_destroy,add='+')
        self.say('你好呀，右键打开陪伴面板。')
        root.after(1000,self.pulse)
    def say(self,text):
        self.app.bubble_text=text; self.app.bubble_until=time.time()+5
        self.last_spoken=time.monotonic()
        if self.panel and self.panel.winfo_exists(): self.speech.set(text)
    def pet(self):
        self.last_action=time.monotonic(); self.app.state='happy'; self.app.happy_until=time.time()+3
        self.say(self.mind.pet(time.time())); self.refresh()
    def feed(self):
        self.last_action=time.monotonic(); self.say(self.mind.feed(time.time())); self.refresh(); self.save()
    def rest(self):
        self.last_action=time.monotonic(); self.app.toggle_state(); self.say(self.app.bubble_text); self.refresh()
    def home(self):
        sw,sh=self.root.winfo_screenwidth(),self.root.winfo_screenheight()
        x,y=self.app.x,self.app.y
        if not math.isfinite(x) or not math.isfinite(y): x,y=180,180
        self.app.x=max(0,min(x,max(0,sw-W))); self.app.y=max(0,min(y,max(0,sh-H-45)))
        self.root.geometry(f'+{int(self.app.x)}+{int(self.app.y)}')
    def save(self):
        try:
            self.mind.advance(time.time())
            data=dict(x=self.app.x,y=self.app.y,move=self.move.get(),top=self.top.get(),quiet=self.quiet.get(),smart=self.smart.get(),mind=self.mind.data(),onboarded=True)
            temp=self.prefs_path.with_suffix('.tmp'); temp.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8'); os.replace(temp,self.prefs_path)
        except (OSError,tk.TclError): updater.log.exception('保存偏好失败')
    def close(self): self.save(); self.root.destroy()
    def on_destroy(self,event):
        if event.widget is self.root: self.save(); self.running=False
    def pulse(self):
        if not self.running:return
        self.mind.advance(time.time())
        if self.deadline is not None and time.monotonic()>=self.deadline:
            self.deadline=None; self.say('这一轮专注完成啦，起来走走吧。')
            if self.panel and self.panel.winfo_exists(): messagebox.showinfo('专注完成','辛苦啦！喝口水，活动一下肩膀。',parent=self.panel)
        if self.smart.get() and not self.quiet.get() and self.deadline is None and self.app.state!='sleep' and time.monotonic()-self.last_spoken>180:
            self.say(self.mind.reply('饿' if self.mind.fullness<25 else '你好',time.localtime().tm_hour))
        self.refresh()
        if int(time.monotonic())%30==0:self.save()
        self.root.after(1000,self.pulse)
    def refresh(self):
        if not self.panel or not self.panel.winfo_exists():return
        self.mood.set('休息中 · 呼噜呼噜' if self.app.state=='sleep' else self.mind.mood(time.localtime().tm_hour))
        self.foodbar['value']=self.mind.fullness; self.bondbar['value']=self.mind.bond
        self.foodtext.set(f'饱腹感 {self.mind.fullness:.0f} / 100'); self.bondtext.set(f'亲密度 {self.mind.bond:.0f} / 100')
        left=max(0,int(self.deadline-time.monotonic())) if self.deadline else 0
        self.clock.set(f'{left//60:02d}:{left%60:02d}' if self.deadline else '准备好再开始')
    def button(self,parent,text,command,primary=False):
        return tk.Button(parent,text=text,command=command,font=(FONT,10),bg=ACCENT if primary else '#EAF0E9',fg='white' if primary else INK,activebackground='#D2E2D5',activeforeground=INK,relief='flat',bd=0,padx=14,pady=10,cursor='hand2',takefocus=True)
    def open_panel(self):
        if self.panel and self.panel.winfo_exists(): self.panel.deiconify(); self.panel.attributes('-topmost',True); self.panel.lift(); return
        w=self.panel=tk.Toplevel(self.root); w.title('社会姐 · 陪伴小屋'); w.configure(bg=BG); w.geometry('520x640'); w.minsize(480,600)
        w.attributes('-topmost',True); w.lift()
        w.protocol('WM_DELETE_WINDOW',w.withdraw)
        head=tk.Frame(w,bg=INK,padx=24,pady=18); head.pack(fill='x')
        tk.Label(head,text='社会姐的陪伴小屋',bg=INK,fg='#F8F5EA',font=(FONT,21,'bold')).pack(anchor='w')
        tk.Label(head,text='一只很有态度，也很在意你的猫。',bg=INK,fg='#C4D9CD',font=(FONT,10)).pack(anchor='w',pady=(5,0))
        style=ttk.Style(w); style.theme_use('clam')
        style.configure('TNotebook',background=BG,borderwidth=0); style.configure('TNotebook.Tab',padding=(20,10),font=(FONT,10))
        style.map('TNotebook.Tab',background=[('selected',CARD)],foreground=[('selected',ACCENT)])
        style.configure('TProgressbar',background=ACCENT,troughcolor='#E7ECE4',borderwidth=0)
        book=ttk.Notebook(w); book.pack(fill='both',expand=True,padx=18,pady=16)
        pages=[]
        for title in ['陪伴','专注','偏好']:
            page=tk.Frame(book,bg=CARD,padx=20,pady=16); book.add(page,text=title); pages.append(page)
        page,focus,settings=pages
        self.mood=tk.StringVar(); self.speech=tk.StringVar(value=self.app.bubble_text)
        tk.Label(page,textvariable=self.mood,bg=CARD,fg=ACCENT,font=(FONT,13,'bold')).pack(anchor='w')
        tk.Label(page,textvariable=self.speech,bg='#F5F3E9',fg=INK,font=(FONT,11),wraplength=380,justify='left',padx=14,pady=16,anchor='w').pack(fill='x',pady=14)
        self.foodtext=tk.StringVar(); self.bondtext=tk.StringVar()
        for var,key in [(self.foodtext,'foodbar'),(self.bondtext,'bondbar')]:
            tk.Label(page,textvariable=var,bg=CARD,fg=MUTED,font=(FONT,9)).pack(anchor='w',pady=(5,4))
            bar=ttk.Progressbar(page,maximum=100); bar.pack(fill='x'); setattr(self,key,bar)
        row=tk.Frame(page,bg=CARD); row.pack(fill='x',pady=16)
        for text,cmd in [('摸摸头',self.pet),('喂小鱼干',self.feed),('休息 / 起床',self.rest)]: self.button(row,text,cmd).pack(side='left',padx=(0,6))
        tk.Label(page,text='跟她说句话',bg=CARD,fg=INK,font=(FONT,10,'bold')).pack(anchor='w')
        row=tk.Frame(page,bg=CARD); row.pack(fill='x',pady=8)
        self.entry=tk.Entry(row,font=(FONT,11),relief='solid',bd=1); self.entry.pack(side='left',fill='x',expand=True,ipady=9,padx=(0,8)); self.entry.bind('<Return>',lambda e:self.send())
        self.button(row,'说给她听',self.send,True).pack(side='right')
        tk.Label(page,text='本机情境回应 · 不联网，不保存聊天内容',bg=CARD,fg=MUTED,font=(FONT,8)).pack(anchor='w')
        tk.Label(focus,text='一起把一件事做好',bg=CARD,fg=INK,font=(FONT,17,'bold')).pack(anchor='w')
        tk.Label(focus,text='计时期间暂停主动台词，结束时温柔提醒。\n关闭程序会结束计时。',bg=CARD,fg=MUTED,font=(FONT,10),justify='left').pack(anchor='w',pady=12)
        self.clock=tk.StringVar(); tk.Label(focus,textvariable=self.clock,bg=CARD,fg=ACCENT,font=(FONT,28,'bold')).pack(pady=28)
        self.minutes=tk.StringVar(value='25'); self.duration=ttk.Combobox(focus,textvariable=self.minutes,values=['15','25','45','60'],state='readonly',width=8); self.duration.pack(pady=10)
        self.button(focus,'开始专注',self.start_focus,True).pack(fill='x',pady=8)
        self.button(focus,'结束本轮',self.stop_focus).pack(fill='x')
        tk.Label(settings,text='让陪伴适合你的节奏',bg=CARD,fg=INK,font=(FONT,15,'bold')).pack(anchor='w',pady=(0,12))
        for text,var,cmd in [('桌面自由走动',self.move,self.apply),('宠物始终置顶',self.top,self.apply),('主动情境台词',self.smart,self.apply),('安静模式（暂停主动台词）',self.quiet,self.apply)]:
            tk.Checkbutton(settings,text=text,variable=var,command=cmd,bg=CARD,fg=INK,activebackground=CARD,font=(FONT,10),selectcolor='#D9E9DE').pack(anchor='w',pady=5)
        self.button(settings,'把社会姐移回屏幕内',self.home).pack(fill='x',pady=10)
        self.button(settings,'检查更新',lambda:self.check_updates(True) if self.check_updates else None).pack(fill='x',pady=5)
        self.button(settings,'打开日志和备份文件夹',lambda:os.startfile(updater.STATE)).pack(fill='x',pady=5)
        tk.Label(settings,text='设置与成长记录仅保存在本机。',bg=CARD,fg=MUTED,font=(FONT,9)).pack(anchor='w',pady=10)
        tk.Label(w,text=f'社会姐 {updater.VERSION}  ·  右键猫咪随时回家',bg=BG,fg=MUTED,font=(FONT,9)).pack(pady=(0,12))
        self.refresh()
    def send(self):
        text=self.entry.get().strip()[:200]
        if not text:return
        self.entry.delete(0,'end'); self.last_action=time.monotonic()
        self.say(self.mind.reply(text,time.localtime().tm_hour))
    def start_focus(self):
        self.deadline=time.monotonic()+int(self.minutes.get())*60; self.say('开始啦，本姐安静陪你。'); self.refresh()
    def stop_focus(self): self.deadline=None; self.say('这轮先到这里，按自己的节奏来。'); self.refresh()
    def apply(self):
        self.app.roaming=self.move.get(); self.root.attributes('-topmost',self.top.get()); self.save()

def main():
    lock=None
    if sys.platform=='win32':
        import msvcrt
        lock=open(updater.STATE/'instance.lock','a+b'); lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
        try: msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        except OSError:
            lock.close(); return
    root=tk.Tk(); companion=Companion(root)
    companion.check_updates=updater.attach(root)
    if len(sys.argv)==3 and sys.argv[1]=='--health':
        root.after(1500,lambda:pathlib.Path(sys.argv[2]).write_text('ready'))
    if not companion.prefs.get('onboarded') and not ('--health' in sys.argv): root.after(700,companion.open_panel)
    # The existing preferences serve as the first-run marker.
    root.mainloop()
    if lock:lock.close()
if __name__=='__main__':
    try:main()
    except Exception:
        updater.log.exception('启动失败')
        raise
