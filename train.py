# @Auther   :Mateo
from ultralytics import YOLO

# 加载预训练模型
model = YOLO('yolov8n.pt')

# 训练模型
model.train(data='./YOLO_Data/data.yaml', epochs=50)