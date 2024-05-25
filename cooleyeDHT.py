from pymongo import MongoClient
import datetime
import Adafruit_DHT
import time

#client = MongoClient('mongodb+srv://raf322:Spark0702@cluster0.fhcw5oz.mongodb.net/')
#db = client.cooleye
#collection = db.tempandhumid

sensor1 = Adafruit_DHT.DHT22
sensor2 = Adafruit_DHT.DHT22
pin1 = 12


while True:
    humidity1, temperature1 = Adafruit_DHT.read_retry(sensor1, pin1)
    

    if temperature1 is not None:
        temp = (9/5 * temperature1) + 32
        
   
    else:
        print("Failed to retrieve temperature data from one of the sensors.")

    if humidity1 is not None:
        hum = humidity1
    else:
        print("Failed to retrieve humidity data from one of the sensors.")

    if temperature1 is not None and humidity1 is not None and humidity2 is not None:
        print(f"Temperature: {temp:.1f} °F, Humidity: {hum:.1f} %")
    else:
        print("Failed to retrieve data from one or both of the DHT22 sensors.")
        
    #data = {
    #"temperature": temp,
    #"humidity": hum
    #}

    #collection.insert_one(data)
    time.sleep(10)
