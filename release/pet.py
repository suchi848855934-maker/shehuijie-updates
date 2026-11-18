# -*- coding: utf-8 -*-
"""
社会姐 - Windows 桌面宠物 V1
仅使用 Python 标准库 Tkinter；Windows 10/11。
"""
import tkinter as tk
from tkinter import messagebox
import math
import random
import time

KEY = "#ff00ff"  # Windows 透明色键
W, H = 260, 290

class SheHuiJie:
    def __init__(self, root):
        self.root = root
        root.title("社会姐")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.configure(bg=KEY)
        try:
            root.wm_attributes("-transparentcolor", KEY)
        except tk.TclError:
            messagebox.showwarning("提示", "当前系统不支持透明色键，窗口背景可能不透明。")
        self.canvas = tk.Canvas(root, width=W, height=H, bg=KEY,
                                highlightthickness=0, bd=0)
        self.canvas.pack()
        self.x, self.y = 180, 180
        self.dx = 1.3
        self.state = "walk"
        self.roaming = True
        self.happy_until = 0
        self.frame = 0
        self.drag = None
        self.last_click = 0
        self.bubble_until = 0
        self.bubble_text = "社会姐驾到！"
        self.menu = tk.Menu(root, tearoff=0)
        self.menu.add_command(label="摸摸头", command=self.pet)
        self.menu.add_command(label="切换状态（走路/睡觉）", command=self.toggle_state)
        self.menu.add_command(label="换一句台词", command=self.say_random)
        self.menu.add_separator()
        self.menu.add_command(label="退出社会姐", command=root.destroy)

        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag_move)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Double-Button-1>", lambda e: self.pet())
        self.canvas.bind("<Button-3>", self.popup)
        self.root.bind("<Escape>", lambda e: root.destroy())
        self.canvas.create_text(130, 274, text="陪伴小屋  ·  点这里", font=("Microsoft YaHei UI", 9), fill="#496654", tags="entry")
        self.draw()
        self.tick()

    def popup(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def start_drag(self, event):
        self.drag = (event.x_root, event.y_root, self.x, self.y)

    def drag_move(self, event):
        if self.drag:
            sx, sy, ox, oy = self.drag
            self.x, self.y = ox + event.x_root - sx, oy + event.y_root - sy
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

    def end_drag(self, event):
        self.drag = None

    def pet(self):
        self.state = "happy"
        self.happy_until = time.time() + 3
        self.bubble_text = random.choice(["摸够了吗？", "本姐今天心情不错。", "给朕拿小鱼干！", "社会姐罩着你！"])
        self.bubble_until = time.time() + 2.8

    def toggle_state(self):
        self.state = "sleep" if self.state != "sleep" else "walk"
        self.bubble_text = "呼噜……" if self.state == "sleep" else "起来巡逻！"
        self.bubble_until = time.time() + 2.5

    def say_random(self):
        self.bubble_text = random.choice([
            "工作归工作，摸鱼也要有技巧。",
            "看什么看，本姐很可爱吗？",
            "今天也要气场全开！",
            "有事喵一声。",
            "别慌，有本姐在。"
        ])
        self.bubble_until = time.time() + 3

    def draw_cat(self):
        c = self.canvas
        c.delete("cat")
        bob = 0 if self.state == "sleep" else math.sin(self.frame * 0.22) * 3
        # 尾巴
        c.create_line(166, 174+bob, 194, 164+bob, 210, 143+bob,
                      smooth=True, splinesteps=20, width=17, fill="#574337",
                      capstyle=tk.ROUND, tags="cat")
        c.create_line(166, 174+bob, 194, 164+bob, 210, 143+bob,
                      smooth=True, splinesteps=20, width=8, fill="#9b7959",
                      capstyle=tk.ROUND, tags="cat")
        # 身体
        c.create_oval(48, 112+bob, 206, 206+bob, fill="#75604d",
                      outline="#3d3029", width=3, tags="cat")
        c.create_oval(67, 129+bob, 183, 198+bob, fill="#f5eee4",
                      outline="", tags="cat")
        # 身体虎斑纹
        for x in (78, 105, 137, 166):
            c.create_arc(x, 116+bob, x+30, 165+bob, start=195, extent=145,
                         style=tk.ARC, outline="#46372f", width=5, tags="cat")
        # 耳朵
        c.create_polygon(61, 82+bob, 67, 28+bob, 108, 68+bob,
                         fill="#75604d", outline="#3d3029", width=3, tags="cat")
        c.create_polygon(151, 68+bob, 196, 28+bob, 198, 89+bob,
                         fill="#75604d", outline="#3d3029", width=3, tags="cat")
        c.create_polygon(73, 69+bob, 72, 43+bob, 94, 69+bob,
                         fill="#d99a91", outline="", tags="cat")
        c.create_polygon(165, 68+bob, 188, 45+bob, 185, 76+bob,
                         fill="#d99a91", outline="", tags="cat")
        # 头
        c.create_oval(48, 53+bob, 208, 174+bob, fill="#8b7258",
                      outline="#3d3029", width=3, tags="cat")
        # 额头纹
        c.create_line(119, 58+bob, 126, 83+bob, 133, 58+bob,
                      fill="#4b3a30", width=5, smooth=True, tags="cat")
        c.create_line(90, 65+bob, 101, 87+bob, fill="#4b3a30", width=4, tags="cat")
        c.create_line(158, 65+bob, 148, 87+bob, fill="#4b3a30", width=4, tags="cat")
        # 白脸颊/口鼻
        c.create_oval(63, 111+bob, 130, 163+bob, fill="#f7f1e9", outline="", tags="cat")
        c.create_oval(124, 111+bob, 194, 163+bob, fill="#f7f1e9", outline="", tags="cat")
        # 眼睛
        if self.state == "sleep":
            c.create_arc(82, 96+bob, 116, 119+bob, start=10, extent=160,
                         style=tk.ARC, outline="#302720", width=4, tags="cat")
            c.create_arc(143, 96+bob, 177, 119+bob, start=10, extent=160,
                         style=tk.ARC, outline="#302720", width=4, tags="cat")
            c.create_text(202, 54+bob, text="Zz", font=("Arial", 14, "bold"),
                          fill="#8a654b", tags="cat")
        else:
            c.create_oval(84, 94+bob, 116, 126+bob, fill="#f8f3e9",
                          outline="#342920", width=2, tags="cat")
            c.create_oval(145, 94+bob, 177, 126+bob, fill="#f8f3e9",
                          outline="#342920", width=2, tags="cat")
            c.create_oval(94, 101+bob, 111, 123+bob, fill="#bd8b35", outline="", tags="cat")
            c.create_oval(151, 101+bob, 168, 123+bob, fill="#bd8b35", outline="", tags="cat")
            c.create_oval(100, 103+bob, 108, 121+bob, fill="#171310", outline="", tags="cat")
            c.create_oval(157, 103+bob, 165, 121+bob, fill="#171310", outline="", tags="cat")
            c.create_oval(102, 104+bob, 106, 109+bob, fill="white", outline="", tags="cat")
            c.create_oval(159, 104+bob, 163, 109+bob, fill="white", outline="", tags="cat")
        # 鼻子、嘴、胡须
        c.create_polygon(119, 129+bob, 132, 129+bob, 125, 137+bob,
                         fill="#d98791", outline="#9f5e68", tags="cat")
        c.create_line(125, 137+bob, 125, 145+bob, fill="#5a453b", width=2, tags="cat")
        c.create_arc(111, 139+bob, 126, 153+bob, start=270, extent=90,
                     style=tk.ARC, outline="#5a453b", width=2, tags="cat")
        c.create_arc(125, 139+bob, 140, 153+bob, start=180, extent=90,
                     style=tk.ARC, outline="#5a453b", width=2, tags="cat")
        for yy in (132, 143, 153):
            c.create_line(65, yy+bob, 101, yy+3+bob, fill="#e9e0d4", width=2, tags="cat")
            c.create_line(151, yy+3+bob, 190, yy+bob, fill="#e9e0d4", width=2, tags="cat")
        # 项圈和名牌
        c.create_arc(78, 146+bob, 179, 187+bob, start=190, extent=160,
                     style=tk.ARC, outline="#d49b27", width=7, tags="cat")
        c.create_oval(111, 165+bob, 145, 188+bob, fill="#e7b84e",
                      outline="#714d1c", width=2, tags="cat")
        c.create_text(128, 176+bob, text="社会姐", font=("Microsoft YaHei", 7, "bold"),
                      fill="#3a2816", tags="cat")
        # 前爪
        c.create_oval(49, 177+bob, 112, 211+bob, fill="#f5eee4",
                      outline="#3d3029", width=2, tags="cat")
        c.create_oval(132, 177+bob, 199, 211+bob, fill="#f5eee4",
                      outline="#3d3029", width=2, tags="cat")
        if self.state == "happy":
            c.create_text(128, 16, text="♥", font=("Arial", 20, "bold"),
                          fill="#e58c9a", tags="cat")

    def draw(self):
        self.draw_cat()
        self.canvas.move("cat", 0, 40)
        if time.time() < self.bubble_until:
            self.canvas.delete("bubble")
            self.canvas.create_rectangle(8, 3, 252, 64, fill="#fff8e9",
                                         outline="#9a7854", width=2,
                                         tags="bubble")
            self.canvas.create_text(130, 33, text=self.bubble_text, width=226,
                                    font=("Microsoft YaHei UI", 9),
                                    fill="#4b3425", tags="bubble")
        else:
            self.canvas.delete("bubble")

    def tick(self):
        self.frame += 1
        if self.state == "walk" and self.roaming and not self.drag:
            self.x += self.dx
            # 轻微来回走动，避免无限跑出屏幕
            sw = self.root.winfo_screenwidth()
            if self.x < 10 or self.x > sw - W - 10:
                self.dx *= -1
                self.x = max(10, min(self.x, max(10, sw-W-10)))
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        if self.state == "happy" and time.time() >= self.happy_until:
            self.state = "walk"
        self.draw()
        self.root.after(90, self.tick)

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SheHuiJie(root)
        root.geometry(f"+{int(app.x)}+{int(app.y)}")
        root.mainloop()
    except Exception:
        import traceback
        try:
            with open("shehuijie_error.log", "w", encoding="utf-8") as log:
                traceback.print_exc(file=log)
        except Exception:
            pass
