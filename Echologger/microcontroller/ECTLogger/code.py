from logger import rp2040_logger
from params import params
import time

# Initiatie the logger
rp = rp2040_logger(params)

# If the microcontroller setup correctly, try to wake the ect
if rp.wakeup_flag == 0:
    rp.setup_ect()

# If we still have no errors, try to connect
attempts = 0
if rp.wakeup_flag == 0:
    while attempts <3: # Make 3 attempts
        a = rp.connect_ect() # try to connect, return the flag (1 is connected, -1 is not)
        if a == 1: # if connected, break
            break
        else: # otherwise wait a walk second and try again
            time.sleep(0.5)

# If we were able to connect, run the 'mission'
if rp.wakeup_flag == 0:
    rp.run_ect()

# DELETE: FOR BENCH TESTING
if rp.wakeup_flag ==1:
    for i in range(5):
        rp.pixel.brightness = 0.5
        rp.pixel[0] = (0,10,0)
        time.sleep(0.5)
        rp.pixel.brightness = 0
        time.sleep(0.5)
else:
    for i in range(2):
        rp.pixel.brightness = 0.5
        rp.pixel[0] = (10,0,0)
        time.sleep(0.5)
        rp.pixel.brightness = 0
        time.sleep(0.5)
    
# Close log, set timer and go to sleep
rp.to_sleep()