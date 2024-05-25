import time
import adafruit_dht
import board
import requests

dht_device1 = adafruit_dht.DHT22(board.D12)
url2 = 'https://protected-dawn-61147-56a85301481c.herokuapp.com/sensor/'

max_retries = 3
successful_read = False  # Flag to track successful reading
count = 0
while count < 50:
    for attempt in range(max_retries):
        try:
            temperature_c = dht_device1.temperature
            temp = temperature_c * (9 / 5) + 32
            hum = dht_device1.humidity
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
    time.sleep(2)
    count = count + 1
