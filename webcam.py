import subprocess
import sys # to access the system
import cv2
 
while True:
    
    subprocess.call(['sh','/home/cooleye/cooleye/python/webcam/webcam.sh'])
    img = cv2.imread("/home/cooleye/cooleye/python/webcam/image.jpg", cv2.IMREAD_ANYCOLOR)
    cv2.imshow("CoolEye", img)
    cv2.waitKey(1)
    sys.exit() # to exit from all the processes
 
cv2.destroyAllWindows() # destroy all windows
