#import io
import threading
import subprocess
import time
import numpy as np
from datetime import datetime
import adafruit_dht
import board
import requests
import json
import sys
import csv
from pymongo import MongoClient
import pyinputplus
import sys, select
import threading
import queue
import cv2
from ultralytics import YOLO
from uuid import UUID, uuid4
#from picamera import PiCamera
#from time import sleep

url1 = "https://protected-dawn-61147-56a85301481c.herokuapp.com/fooditem/"
url2 = 'https://protected-dawn-61147-56a85301481c.herokuapp.com/sensor/'
url3 = 'https://protected-dawn-61147-56a85301481c.herokuapp.com/image/upload'

def listen_for_barcode_input(barcode_queue):
        while True:
                try:
                        barcode_input = input("")
                        barcode_queue.put(barcode_input)
                except EOFError:
                        # This can happen if the input stream is closed, indicating the program is likely shutting down.
                        break

class RaspberryPiController:
    def __init__(self):
        print("Initializing")
        self.live_feed_trigger_value = False
        self.current_section = "Startup"
        self.last_input_time = None
        client = MongoClient('mongodb+srv://raf322:Spark0702@cluster0.fhcw5oz.mongodb.net/')
        self.db = client.cooleye
        self.collection = self.db.fooditems
        self.dht_device = adafruit_dht.DHT22(board.D12)
        self.barcode_queue = queue.Queue()
        self.barcode_listener_thread = threading.Thread(target=listen_for_barcode_input, args=(self.barcode_queue,))
        self.barcode_listener_thread.daemon = True  # Optional: makes the thread exit when the main program exits
        self.barcode_listener_thread.start()
        self.last_input_time = time.time()

    def check_time_and_date(self):
        print("Current time and date verified:", datetime.now())

    def update_packages(self):
        #subprocess.run(["sudo", "apt-get", "update"], check=True)
        #subprocess.run(["sudo", "apt-get", "upgrade", "-y"], check=True)
        print("Packages Updated")
        
        
    def action_every_hour(self):
        print("Hourly action executed")
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
                       data = {
                           "unique_id": str(uuid4()),
                           "Item": label,
                           "Count": int(target_counts[label]),
                           "expiration_date": None
                       }
                    
                       # Send the label to MongoDB
                       #self.collection.insert_one(data)
                    
                       # Reset the count
                       target_counts = {label: 0 for label in target_classes}
                       '''
                       if label == 'apple' or label == 'orange':
                               days = 28
                       elif label ==  'cabbage' or label == 'potato' or label == 'pomegranate':
                               days = 56
                       elif label == 'asparagus' or label == 'pear' or label == 'peach' or label == 'broccoli':
                               days = 4
                       elif label == 'mango' or label == 'watermelon' or label == 'lemon' or label == 'grape bunch':
                               days = 14
                       elif label == 'bell pepper' or label == 'strawberry' or label == 'cucumber' or label == 'pineapple' or label == 'zucchini':
                               days = 7
                       elif label == 'carrot' or 'cantaloupe':
                               days = 21
                       else:
                               days = 5
                       '''
                       try:
                          response = requests.post(url1, json=data)
                          if response.status_code == 200:
                             print("Data successfully sent to server.")
                          else:
                             print(f"Failed to send data. Status code: {response.status_code}")
                       except requests.RequestException as e:
                          print(f"An error occurred: {e}")


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

        
    def read_dht22(self):
        try:
                temperature_c = self.dht_device.temperature
                humidity = self.dht_device.humidity
                if temperature_c is not None and humidity is not None:
                        return {"temperature": temperature_c, "humidity": humidity}
                else:
                        print("Failed to retrieve data from humidity sensor")
                return None
        except RuntimeError as error:
                print(error.args[0])
                return None
            
                    
                    
    def action_every_five_minutes(self):
        print("5-minute action executed")
        max_retries = 3
        successful_read = False  # Flag to track successful reading
        for attempt in range(max_retries):
                try:
                        temperature_c = self.dht_device.temperature
                        temp = temperature_c * (9 / 5) + 32
                        hum = self.dht_device.humidity
                        print(f"Temp:{temperature_c:.1f} C / {temp:.1f} F    Humidity: {hum}%")
                        # Prepare the data after a successful read
                        data = {
                                "temperature": temp,
                                "humidity": hum
                        }
                        successful_read = True  # Mark read as successful
                        break  # Exit the loop after a successful read
                except RuntimeError as e:
                        print(f"Error reading from DHT sensor: {e}")
                        if attempt < max_retries - 1:
                                print("Retrying...")
                                time.sleep(2)  # Wait a bit before retrying
            # Check if read was successful before attempting to send data
        if successful_read:
                try:
                        response = requests.post(url2, json=data)
                        if response.status_code == 200:
                                print("Data successfully sent to server.")
                        else:
                                print(f"Failed to send data. Status code: {response.status_code}")
                except requests.RequestException as e:
                        print(f"An error occurred: {e}")
        else:
                print("Failed to read from DHT sensor after several attempts.")

        


    def start_rest_section(self):
        self.current_section = "Rest"
        print("Scanning in Rest")
        counter = 0
        count = 0
        counting = 0
        while self.current_section == "Rest":
                # Perform scheduled actions
                if counter >= 3:
                        self.get_picture()
                        counter = 0
                if count >= 2:
                        self.action_every_five_minutes()
                        count = 0
                
                if counting >= 4:
                        self.action_every_hour()
                        counting = 0
                        
                # Check for new barcode input
                try:
                        barcode = self.barcode_queue.get_nowait()  # Non-blocking get
                        #print(f"Barcode scanned: {barcode}")
                        '''
                        if barcode == 1695024:
                                self.action_every_hour()
                                pass
                        '''
                        if barcode != None:
                                self.start_scanning_section()
                        
                        # Process the barcode as needed
                except queue.Empty:
                        # No barcode was scanned, proceed with other tasks
                        pass
        
                # Sleep for a short time to prevent high CPU usage
                time.sleep(5)
                counter = counter + 1
                count = count + 1
                counting = counting + 1

        #client = MongoClient('mongodb+srv://raf322:Spark0702@cluster0.fhcw5oz.mongodb.net/')
        #db = client.cooleye
        #collection = db.barcodes
        """try:
                barcode_input = pyinputplus.inputStr(prompt="Scan a barcode: ", default=None, timeout=5)
                if barcode_input:
                        self.start_scanning_section()
        #barcode_input = input("Scan a barcode: ")
        except pyinputplus.TimeoutException:
                while self.current_section == "Rest":
                        self.action_every_hour()
                        for _ in range(12):  # 12 * 5 minutes = 60 minutes
                                if self.current_section != "Rest":
                                        break
                                self.action_every_five_minutes()
                                time.sleep(5)  # Sleep for 5 minutes
                        if barcode_input:
                                self.start_scanning_section()"""

    def start_scanning_section(self):
        self.current_section = "Scanning"
        self.last_input_time = time.time()
        print("Now in Scanning Mode")
        print("Scan a barcode: ")

        while self.current_section == "Scanning":
                try:
                        # Attempt to get a barcode from the queue in a non-blocking manner
                        barcode_input = self.barcode_queue.get_nowait()
                        print(f"Processing barcode: {barcode_input}")
                        self.last_input_time = time.time()
                        # Example condition to switch back to rest section or handle barcode logic
                        if barcode_input == "1695023":
                                self.start_rest_section()
                        if barcode_input != None:
                                self.last_input_time = time.time()
                                self.process_barcode(barcode_input)
                except queue.Empty:
                # No new barcode input, continue with other tasks
                        pass
                #while self.current_section == "Scanning":
                if time.time() - self.last_input_time > 45:  # 20 minutes without input
                        self.start_rest_section()
                #else:
                        #self.start_scanning_section()
        # Sleep briefly to avoid overwhelming the CPU
        time.sleep(5)

    def process_barcode(self, barcode):
    # This method should contain the logic to process the barcode
    # For illustration, let's simulate an API call as you previously had
        send_data = {}
        params = {
                'api_key': 'DA2E881C539445868AD19CE7489198C2',
                'type': 'product',
                'gtin': barcode,
                'output': 'csv',
                'csv_fields': 'product.title',
        }
        try:
                api_result = requests.get('https://api.bluecartapi.com/request', params)
                data = api_result.content.decode('utf-8')
                first_line_break = data.find('\n')

                if first_line_break != -1:
                        name = data[first_line_break+1:].strip()
                        print("Product name: ", name)
                        send_data = {
                        "unique_id": str(uuid4()),
                        "Item": name,
                        "Count": 1,
                        "expiration_date": datetime.now()
                        
                        }
            
        except requests.RequestException as e:
                print(f"Error making API request: {e}")
        if send_data:
                self.collection.insert_one(send_data)
        else:
                print("No product name extracted or API call failed.")
        barcode_input = None
        # Wait 5 seconds so it isnt constantly doing this trash
        #time.sleep(5)
        # Simulate detecting input

        """self.current_section = "Scanning"
        print("Now in Scanning Mode")
        barcode_input = input("Scan a barcode: ")
        self.last_input_time = time.time()
        if barcode_input == "1695023":
                barcode_input == None
                self.start_rest_section()

        params = {
            'api_key': 'DA2E881C539445868AD19CE7489198C2',
            'type': 'product',
            'gtin': barcode_input,
            'output': 'csv',
            'csv_fields': 'product.title',
            }
        api_result = requests.get('https://api.bluecartapi.com/request', params)
        data = api_result.content.decode('utf-8')

        # Immediately find the first line break after decoding data
        first_line_break = data.find('\n')
    
        send_data = None  # Initialize send_data with None to ensure it's always defined
        if first_line_break != -1:
                name = data[first_line_break+1:].strip()  # Use strip() to remove any leading/trailing whitespace
                print(name)  # Print the name extracted from data
                send_data = {
        
                "name": name
                }

        # Check if send_data has been populated before attempting to insert into MongoDB
        if send_data:
                self.collection.insert_one(send_data)
        else:
                print("No product name extracted or API call fqt.qpa.plugin: Could not find the Qt platform plugin "wayland" in "/home/cooleye/cooleye/cooleye/lib/python3.11/site-packages/cv2/qt/plugins"
Failed to grab frame
ailed.")
                
        #collection.insert_one(send_data)
        barcode_input = None
        # Wait 5 seconds so it isnt constantly doing this trash
        time.sleep(5)
        # Simulate detecting input
        while self.current_section == "Scanning":
                if time.time() - self.last_input_time > 1200:  # 20 minutes without input
                        self.start_rest_section()
                else:
                        self.start_scanning_section()"""
                
    def get_picture(self):
        url3 = 'https://protected-dawn-61147-56a85301481c.herokuapp.com/image/upload'

        subprocess.call(['sh','/home/cooleye/cooleye/python/webcam/webcam.sh'])
        
        img_file = {'file': open('/home/cooleye/cooleye/python/webcam/image.jpeg', 'rb')} 

        print(type(img_file))

        try:
           response = requests.post(url3, files=img_file)
           if response.status_code == 200:
                 print("Picture successfully sent to server.")
           else:
                 print(f"Failed to send data. Status code: {response.status_code}")
        except requests.RequestException as e:
                 print(f"An error occurred: {e}")
        

    def startup_tasks(self):
        self.check_time_and_date()
        self.update_packages()
        self.start_rest_section()

    def run(self):
        self.startup_tasks()

if __name__ == "__main__":
    controller = RaspberryPiController()
    # Run the Raspberry Pi controller in a separate thread to keep the main thread free
    # for other tasks or to gracefully handle shutdown signals.
    threading.Thread(target=controller.run).start()
