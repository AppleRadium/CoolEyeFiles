from ultralytics import YOLO

# Load the model
model = YOLO("yolov8n.yaml")  # Example: Load YOLOv8 Nano pretrained model

# Print class names

model.train(data="/home/cooleye/cooleye/python/ultralytics/ultralytics/cfg/datasets/coco128.yaml", epochs=3)
