import pathlib, sys, tkinter as tk
from pet import SheHuiJie
import updater
root=tk.Tk()
app=SheHuiJie(root)
updater.attach(root)
if len(sys.argv)==3 and sys.argv[1]=='--health':
    root.after(1500, lambda: pathlib.Path(sys.argv[2]).write_text('ready'))
root.mainloop()
