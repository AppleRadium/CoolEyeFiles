import subprocess
import sys
import time

subprocess.call(['sh', 'usb_off.sh'])

start = time.time()
while time.time() - start < 5:
    pass

subprocess.call(['sh', 'usb_on.sh'])
