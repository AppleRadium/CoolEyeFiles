import cv2
import numpy as np
import time


def load_yolo():
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers().flatten()]
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    return net, classes, output_layers

def detect_objects(frame, net, output_layers):
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)
    return outs

def get_box_dimensions(outs, height, width):
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)
            x = int(center_x - w / 2)
            y = int(center_y - h / 2)
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))
            class_ids.append(class_id)
    return boxes, confidences, class_ids

def draw_labels(boxes, confidences, classes, class_ids, frame):
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    label_vector = []
    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            if label in ["apple", "orange", "banana", "strawberry"]:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y + 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, (0, 255, 0), 3)
                font_scale = 0.25
                label_vector.append(label)
                print(label)
            #print(label_vector)

def capture_frames():
    net, classes, output_layers = load_yolo()
    cap = cv2.VideoCapture(0)
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_id  += 1
        if frame_id % 5 != 0:
            continue
        
        frame = cv2.resize(frame, (640, 480))
        outs = detect_objects(frame, net, output_layers)
        boxes, confidences, class_ids = get_box_dimensions(outs, frame.shape[0], frame.shape[1])
        draw_labels(boxes, confidences, classes, class_ids, frame)

        cv2.imshow('Frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Run the function
capture_frames()
