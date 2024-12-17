from logger import rp2040_logger
from params import params
import alarm
import time

# Initiatie the logger
try:
    rp = rp2040_logger(params)
except: # If we fail to start up, just go back to sleep using the 'no clock' waiting period using the internal time alarm
    time_alarm = alarm.time.TimeAlarm(monotonic_time = time.monotonic()+(params.wakeup_interval*60))
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)

# If the microcontroller setup correctly, try to wake the ect
if rp.status_flag == 0:
    rp.setup_ect()

# If we still have no errors, try to connect
if rp.status_flag == 0:
    a = rp.connect_ect() # try to connect, return the flag (1 is connected, -1 is not)

# If we were able to connect, run the 'mission'
if rp.status_flag == 0:
    rp.run_ect()
    
# Close log, set timer and go to sleep
rp.to_sleep()