# @Auther   :Mateo
# ==============================================
# 一体化服务：Flask网页 + FastAPI异地接口
# 运行一个文件即可同时启动两个服务
# ==============================================
import os
import time
import threading
import pandas as pd
from PIL import Image
from werkzeug.utils import secure_filename

# Flask 相关
from flask import Flask, render_template, request, jsonify, send_file

# FastAPI 相关
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn

# 导入你的识别文件 A.py
import lincese_plate

# ====================== 全局配置 ======================
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp"}
record_list = []  # 识别记录

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ====================== 图片缩放 ======================
def resize_image(image_path, target_height=400):
    try:
        img = Image.open(image_path)
        w, h = img.size
        new_w = int(w * target_height / h)
        img = img.resize((new_w, target_height), Image.Resampling.LANCZOS)
        img.save(image_path)
    except:
        pass

# ====================== 【服务1】Flask 网页服务 ======================
flask_app = Flask(__name__)
flask_app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@flask_app.route("/")
def index():
    return render_template("index.html")

@flask_app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    if not file or file.filename == "":
        return jsonify({"code": 400})

    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(path)
    resize_image(path)

    plate = lincese_plate.process_and_recognize(path)
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    record_list.append({"time": now, "plate": plate})

    return jsonify({"code": 200, "plate": plate, "time": now})

@flask_app.route("/get_records")
def get_records():
    return jsonify(record_list)

@flask_app.route("/download")
def download():
    df = pd.DataFrame(record_list)
    df.columns = ["识别时间", "车牌号码"]
    save_path = "识别记录.xlsx"
    df.to_excel(save_path, index=False)
    return send_file(save_path, as_attachment=True)

# ====================== 【服务2】FastAPI 异地接口 ======================
fast_app = FastAPI(title="车牌识别系统")

@fast_app.post("/api/plate/recognize")
async def recognize_api(file: UploadFile = File(...)):
    try:
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)

        # 读取流 → 写入本地 → 重组图片
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)

        resize_image(save_path)
        plate = lincese_plate.process_and_recognize(save_path)
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        record_list.append({"time": now, "plate": plate})

        return {
            "code": 200,
            "msg": "识别成功",
            "plate_number": plate,
            "time": now
        }
    except Exception as e:
        return {"code": 500, "msg": f"错误：{str(e)}", "plate_number": None}

# ====================== 一键启动双服务 ======================
def run_flask():
    flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

def run_fastapi():
    uvicorn.run(fast_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    print("=" * 50)
    print(" 车牌识别服务启动成功 ")
    print(" 网页端：http://127.0.0.1:5000")
    print(" 接口端：http://127.0.0.1:8000")
    print(" 接口文档：http://127.0.0.1:8000/docs")
    print("=" * 50)

    # 多线程同时启动 Flask 和 FastAPI
    t1 = threading.Thread(target=run_flask, daemon=True)
    t2 = threading.Thread(target=run_fastapi, daemon=True)

    t1.start()
    t2.start()

    # 保持主程序运行
    while True:
        time.sleep(1)