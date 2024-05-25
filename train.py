from ultralytics import YOLO

# For training a new model from scratch or fine-tuning
model = YOLO('yolov8n.pt')  # Specify the model configuration you wish to use

# Start training
results = model.train(data="/home/cooleye/cooleye/python/yolov8n/training/config.yaml", 
                      epochs=1)
