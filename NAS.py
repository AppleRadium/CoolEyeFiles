from ultralytics import NAS
model = NAS('/home/cooleye/cooleye/python/yolo_nas_s.pt')
model.info()
results = model.val(data='coco8.yaml')
