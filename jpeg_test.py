import subprocess
import cv2
import requests



print("hello")
url3 = 'https://protected-dawn-61147-56a85301481c.herokuapp.com/image/upload'

subprocess.call(['sh','/home/cooleye/cooleye/python/webcam/webcam.sh'])
#img = cv2.imread("/home/cooleye/cooleye/python/webcam/image.jpg", cv2.IMREAD_ANYCOLOR)
img_file = {'file': open('/home/cooleye/cooleye/python/webcam/image.jpeg', 'rb')} #change this to any .jpeg on local for testing

print(type(img_file))

try:
    response = requests.post(url3, files=img_file)
    if response.status_code == 200:
        print("Picture successfully sent to server.")
    else:
        print(f"Failed to send data. Status code: {response.status_code}")
except requests.RequestException as e:
    print(f"An error occurred: {e}")
