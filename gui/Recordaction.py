from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import scrolledtext
from tkinter import colorchooser

class RecordWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("行为元录制")
        self.master.geometry("400x400") 

        self.frame = Frame(self.master)
        self.frame.pack(padx=10, pady=10)

        self.label = Label(self.frame, text="行为元录制")
        self.label.grid(row=0, column=0, padx=5, pady=5) 

        self.start_button = Button(self.frame, text="开始录制", command=self.start_recording)
        self.start_button.grid(row=1, column=0, padx=5, pady=5)

        self.stop_button = Button(self.frame, text="停止录制", command=self.stop_recording)
        self.stop_button.grid(row=1, column=1, padx=5, pady=5) 

        self.action_select_mode = Frame(self.master)
        self.action_select_mode.pack(padx=10, pady=10)

        self.action_select_mode_label = Label(self.action_select_mode, text="行为元选择模式")
        self.action_select_mode_label.grid(row=0, column=0, padx=5, pady=5)

        self.action_select_mode_combobox = ttk.Combobox(self.action_select_mode, values=["单击", "按下/释放"])
        self.action_select_mode_combobox.grid(row=0, column=1, padx=5, pady=5)

        self.action_select_mode_combobox.current(0)

        self.action_select_mode_combobox.bind("<<ComboboxSelected>>", self.on_action_select_mode_changed)

    def on_action_select_mode_changed(self, event):
        pass
    def start_recording(self):
        pass
    def stop_recording(self):
        pass

if __name__ == "__main__":
    root = Tk()
    app = RecordWindow(root)
    root.mainloop()