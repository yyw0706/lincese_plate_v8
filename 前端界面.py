import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import threading
import lincese_plate


# ====================== Tkinter 界面（不变） ======================
class PlateRecognitionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("车牌识别系统")
        self.root.geometry("900x500")
        self.root.resizable(False, False)

        self.img_path = None
        self.display_img = None

        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 左侧：图片上传区域
        self.left_frame = ttk.LabelFrame(main_frame, text="图片上传区域", width=420, height=400)
        self.left_frame.grid(row=0, column=0, padx=10)
        self.left_frame.grid_propagate(False)

        self.img_label = ttk.Label(self.left_frame)
        self.img_label.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        self.upload_btn = ttk.Button(
            self.left_frame,
            text="选择车牌图片",
            command=self.upload_image
        )
        self.upload_btn.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

        # 右侧：识别结果区域
        self.right_frame = ttk.LabelFrame(main_frame, text="识别结果区域", width=420, height=400)
        self.right_frame.grid(row=0, column=1, padx=10)
        self.right_frame.grid_propagate(False)

        ttk.Label(self.right_frame, text="识别结果", font=("微软雅黑", 18)).place(relx=0.5, rely=0.3, anchor=tk.CENTER)
        self.result_label = ttk.Label(self.right_frame, text="等待识别...", font=("微软雅黑", 40, "bold"),
                                      foreground="red")
        self.result_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return

        self.img_path = file_path

        # 显示预览
        try:
            img = Image.open(file_path)
            img.thumbnail((380, 300))
            self.display_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.display_img)
        except:
            self.result_label.config(text="图片加载失败")
            return

        self.result_label.config(text="识别中...")
        threading.Thread(target=self.run_recognize, daemon=True).start()


    def run_recognize(self):
        try:
            # 调用 A.py 里的识别函数
            plate_number = lincese_plate.process_and_recognize(self.img_path)

            # 把结果显示到界面
            self.root.after(0, lambda: self.result_label.config(text=plate_number))
        except Exception as e:
            self.root.after(0, lambda: self.result_label.config(text="识别失败"))


# ====================== 启动 ======================
if __name__ == "__main__":
    root = tk.Tk()
    app = PlateRecognitionGUI(root)
    root.mainloop()