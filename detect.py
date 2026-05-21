# @Auther   :Mateo
from ultralytics import YOLO

if __name__ == "__main__":
    pth_path = r"D:\python_code\v8车牌检测\weights\best.pt"

    test_path = r"D:\python_code\v8车牌检测\runs\detect_test"
    # Load a models
    # models = YOLO('yolov8n.pt')  # load an official models
    model = YOLO(pth_path)  # load a custom models

    # Predict with the models
    results = model(test_path, save=True, conf=0.5)  # predict on an image
