import time, unittest
from launcher import Mind
class MindTests(unittest.TestCase):
    def test_corrupt_memory(self):
        m=Mind({'fullness':'bad','bond':float('nan'),'last':None},now=1000)
        self.assertEqual(m.fullness,75); self.assertEqual(m.bond,10)
    def test_offline_decay_clamped(self):
        m=Mind({'fullness':100,'last':0},now=10000000)
        self.assertEqual(m.fullness,28)
    def test_feed_cooldown(self):
        m=Mind({'fullness':20},now=1000)
        m.feed(1000); before=m.fullness; m.feed(1001)
        self.assertLessEqual(m.fullness,before)
    def test_fullness_cap(self):
        m=Mind({'fullness':90},now=1000); m.feed(1000)
        self.assertEqual(m.fullness,100)
    def test_context(self):
        m=Mind(now=1000)
        self.assertIn('专注',m.reply('我要学习',10))
        self.assertIn('歇',m.reply('今天有点累',10))
        self.assertIn('困',m.mood(1))
if __name__=='__main__':unittest.main()

