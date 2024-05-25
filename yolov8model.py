import cv2
from ultralytics import YOLO
from pymongo import MongoClient
import requests

#this section has not been tested but its essentially the same from before
#client = MongoClient('mongodb+srv://raf322:Spark0702@cluster0.fhcw5oz.mongodb.net/')
#db = client.cooleye
#collection = db.fooditems
#url = "https://protected-dawn-61147-56a85301481c.herokuapp.com/fooditem/"
def capture_frames_and_detect():
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Load YOLOv8 model
    model = YOLO("/home/cooleye/cooleye/python/train14/weights/best.pt")  

    # Specify the classes you want to detect
    target_classes = ["strawberry", "bell pepper", "pineapple", "lemon"]
    
    # This part also not tested. Meant to keep track of number of target_classes in a given frame. Can't access the output data that shows the count directly unfortunately
    target_counts = {label: 0 for label in target_classes}

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # The frame captured by cv2 is in BGR format and needs to be converted to RGB
        #frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Detect objects in the frame
        results = model.predict(source=frame)

        # Assuming results is a list of result objects for each frame
        for result in results:
            # Iterate over each detection
            for i, box in enumerate(result.boxes.xyxy):
                cls_id = int(result.boxes.cls[i])
                label = model.names[cls_id]
               # data = {
                    #"name": label
                #}
                
                #response = requests.post(url, json=data)
                #if response.status_code == 200:
                #    print("Data successfully sent to server.")
               # else:
                #    print(f"Failed to send data. Status code: {response.status_code}")
                    
                # Filter detections by target classes
                if label in target_classes:
                    # Iterate the count (not tested)
                    target_counts[label] += 1
                    
                    # Unpack bounding box coordinates and convert to int
                    x1, y1, x2, y2 = map(int, box)
                    conf = result.boxes.conf[i]

                    # Draw rectangle and label on the frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    
                    # Organize the data for sending to MongoDB
                   # data = {
                     #   "name": label
                    #}
            
                
                    # Send the label to MongoDB
                    #collection.insert_one(data)
                    
                    # Reset the count
                    target_counts = {label: 0 for label in target_classes}

        # Convert the frame back to BGR format for displaying
        #frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Display the resulting frame with detections
        cv2.imshow('YOLOv8 Detection', frame)
        
        
        # Break the loop with 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_frames_and_detect()
