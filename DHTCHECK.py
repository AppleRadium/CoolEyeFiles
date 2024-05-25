import pigpio
import time
import DHT22

# Initialize pigpio library
pi = pigpio.pi()

# Specify the GPIO pin connected to your DHT22 sensor
sensor_gpio = 12

# Initialize the DHT22 sensor
sensor = DHT22.sensor(pi, sensor_gpio)

def read_dht22():
    """Reads humidity and temperature from the DHT22 sensor."""
    sensor.trigger()
    time.sleep(0.2)  # Wait for 200 ms for the sensor to process the data
    
    # Get the humidity and temperature readings
    humidity = '%.2f' % (sensor.humidity())
    temperature = '%.2f' % (sensor.temperature())
    
    print(f"Humidity: {humidity}%")
    print(f"Temperature: {temperature}C")

try:
    while True:
        read_dht22()
        time.sleep(3)  # Wait for 3 seconds before reading again
except KeyboardInterrupt:
    pass
finally:
    sensor.cancel()
    pi.stop()
