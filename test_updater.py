import hashlib, json, os, pathlib, tempfile, unittest, zipfile
from unittest.mock import patch
import updater as u
class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base=pathlib.Path(self.tmp.name); self.state=self.base/'state'; self.state.mkdir()
        self.old=u.STATE; u.STATE=self.state; self.addCleanup(setattr,u,'STATE',self.old)
    def package(self, contents=None):
        path=self.state/'download.zip'
        with zipfile.ZipFile(path,'w') as z:
            for n in u.FILES: z.writestr(n,(contents or {}).get(n,'new'))
        (self.state/'download.sha256').write_text(hashlib.sha256(path.read_bytes()).hexdigest())
        return path
    def test_traversal(self):
        p=self.package()
        with zipfile.ZipFile(p,'a') as z: z.writestr('../escape','x')
        with self.assertRaises(ValueError): u.unpack(p,self.base/'stage')
    def test_hash_rechecked(self):
        p=self.package(); p.write_bytes(b'tampered')
        with self.assertRaises(ValueError): u.install(self.base,0)
    def test_rollback(self):
        self.package(); target=self.base/'app'; target.mkdir()
        for n in u.FILES: (target/n).write_text('original')
        with patch.object(u.subprocess,'Popen',side_effect=[OSError('injected launch failure'),object()]):
            u.install(target,0)
        for n in u.FILES: self.assertEqual((target/n).read_text(),'original')
        self.assertEqual(len(list(self.state.glob('backup-*'))),1)
    def test_success(self):
        self.package(); target=self.base/'app'; target.mkdir()
        for n in u.FILES: (target/n).write_text('original')
        def launch(args,**kw):
            pathlib.Path(args[-1]).write_text('ready')
            return object()
        with patch.object(u.subprocess,'Popen',side_effect=launch): u.install(target,0)
        for n in u.FILES: self.assertEqual((target/n).read_text(),'new')
    def test_version(self): self.assertGreater(u.version('1.10.0'),u.version('1.9.0'))
    def test_offline(self):
        with patch.object(u,'fetch',side_effect=OSError('offline')):
            with self.assertRaises(OSError): u.check()
if __name__=='__main__': unittest.main()
