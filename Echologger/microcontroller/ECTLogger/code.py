import time
import os
import board
import busio
import neopixel
import digitalio
import rtc
import storage

import adafruit_sdcard
import adafruit_ina260
import adafruit_ds3231
import adafruit_logging as logging
from adafruit_logging import FileHandler

import echosounder as echo
from params import params

# Set up the neopixel just so we can see whats happening on the bench
pixels = neopixel.NeoPixel(board.NEOPIXEL, 1,brightness = .5) # REMOVE FOR DEPLOYMENT
pixels[0] = (0, 0, 10) # REMOVE FOR DEPLOYMENT

# Power on the i2c peripherals via a GPIO
pwr_i2c = digitalio.DigitalInOut(board.D12)
pwr_i2c.direction = digitalio.Direction.OUTPUT
pwr_i2c.value = True
time.sleep(.05)

# Scna for the i2c peripherals
i2c = board.I2C()

# Connect to the DS3231 and set the internal rtc
rtc_ext = adafruit_ds3231.DS3231(i2c)
rtc_int = rtc.RTC()
rtc_int.datetime = rtc_ext.datetime

# Format the datetime for the file basename
def _format_datetime(datetime):
    return "D{:02}{:02}{}-T{:02}{:02}{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )
file_datetime = _format_datetime(rtc_int.datetime)

def toSleep(sleep_flag, logger, file_handler, dt):
    
    if sleep_flag == 1:
        msg = ' - Successful wakeup, going to sleep'
    elif sleep_flag == -1:
        msg = ' - Unsuccessful wakeup, going to sleep'
    elif sleep_flag == 2:
        msg = ' - Wake up earlier than mission start, skipping cycle and going to sleep'
    elif sleep_flag == 3:
        msg = ' - Wake up after mission end, going to sleep and deinitializing alarm'
    elif sleep_flag == 4:
        msg = ' - Voltage below ECT minimum, skipping cycle and going to sleep'

    if sleep_flag ==1:
        logger.info(dt+msg)
    else:
        logger.warning(dt+msg)
    file_handler.close()
    
    # go to sleep
    if sleep_flag == 3:
        pass
        # deinit alarm and go to sleep
    else:
        pass
        # reinit alarm and go to sleep


# mount the SD card
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
time.sleep(0.05)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Now connect to the ina260 to get the current voltage
ina260 = adafruit_ina260.INA260(i2c)

#initiate logger
logger = logging.getLogger(params.deployment)
file_handler = FileHandler(params.log_file)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
logger.info(file_datetime+' - Awake, V:'+str(ina260.Voltage))

# First check that we woke up during the time we're supposed to be collecting data
if (time.mktime(rtc_int.datetime)-time.mktime(time.struct_time(params.start_time))) < 0:
    #if the value is negative, it means we haven't hit the start time yet
    toSleep(2, logger, file_handler, _format_datetime(rtc_int.datetime))
if (time.mktime(time.struct_time(params.end_time))-time.mktime(rtc_int.datetime)) < 0:
    #if the value is negative, it means we passed the end time
    toSleep(3, logger, file_handler, _format_datetime(rtc_int.datetime))

#### If we're continuing...

# Check for the number of binary files we've already written and iterate the counter
files = os.listdir('/sd')
# the counter is the number of files, divided by the number of configs
log_ct = int(sum(['.bin' in f for f in files])/len(params.config)) 

#***Turn on the ECT***
# Initiate the uart
uart = busio.UART(board.TX, board.RX, baudrate=115200,timeout=.1,receiver_buffer_size=16448)

# ADD: Power on the ECT by gorunding the MOSFET
pwr_ect = digitalio.DigitalInOut(board.D10) # Set the D10 pin as the grounding pin
pwr_ect.direction = digitalio.Direction.OUTPUT # Set to output
pwr_ect.value(0) # Immediately make sure it is off
time.sleep(.05)
pwr_ect.value(1) # Turn it on and wait before trying to connect
time.sleep(.5)

# Check the voltage once the ECT is powered
if ina260.voltage < params.minimum_voltage:
    pwr_ect.value(0) # immediatel depower
    #if the voltage is below what can run the echologger, go back to sleep and try again later
    toSleep(4, logger, file_handler, _format_datetime(rtc_int.datetime))
    pixels[0] = (10, 0, 0) # delete


# If it should have enough juice....
# Try to connect, which will also make sure we stop it from pinging if it turned on
ect = echo.Echosounder(uart,pixels)
# Make sure it's definitely not pinging
try:
    ect.Detect()
except:
    ect.Detect()

# Set the time on the ECT, which it will write into the ping data
ect.SetValue("IdTime",str(int(time.mktime(rtc_int.datetime))))
time.sleep(.2)
pixels[0] = (0, 10, 0)


# Collect the data files
for k in params.config.keys(): # for each configuration
    # iterate through the config settings and set the values
    for item in params.config[k].items(): 
        ect.SetValue(item[0],item[1])
        time.sleep(0.05)
    
    # Assign the basename to use for all files with the same configuration
    file_basename = '/sd/'+params.deployment+'_'+file_datetime+'_'+k+'_'+str(log_ct)

    # Dump out the 'info' into a text file
    ect.recordInfo(file_basename+'.txt')
    pixels[0] = (10, 0, 0)

    # record
    ect.recordPings(file_basename+'.bin',numPings=params.numPings[k], maxTime=params.maxTime[k])
    pixels[0] = (0, 0, 10)

# Turn the power back off
pwr_ect.value(0)

# Check that there's a new .bin file that contains the file_basename date in it
files = os.listdir('/sd') # scan the sd card again
if (sum([file_basename in f for f in files])) > 1: # there should be at least 2
    toSleep(-1, logger, file_handler, _format_datetime(rtc_int.datetime))

# If we made it all the way to the end without issue...
toSleep(1, logger, file_handler, _format_datetime(rtc_int.datetime))