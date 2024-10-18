import time
import os
import board
import busio
import neopixel
import digitalio
import rtc
import storage
import alarm
import math

import adafruit_sdcard
import adafruit_ina260
import adafruit_ds3231
import adafruit_logging as logging
from adafruit_logging import FileHandler

import echosounder as echo
from params import params

class rp2040_logger():

    def __init__(self,params):
        self.status_flag = 0
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1,brightness = .5)
        self.params = params
        self.initiate_logger()
        flashpixel(self.pixel,3,(10,10,10))

        self.i2c_pwr()
        time.sleep(.05)
        self.set_clock()
        
        self.set_ina()

        self.file_datetime = _format_datetime(time.localtime(self.start_time))

        self.logger.info(self.file_datetime+' - Awake, V:'+str(self.ina260.voltage))
        
        try:
            self.mount_sd()
        except:
            self.status_flag = 5
            print('Unable to mount SD, sleep')
            self.to_sleep()
        
        # First check that we woke up during the time we're supposed to be collecting data
        if (self.start_time-time.mktime(time.struct_time(self.params.start_time))) < 0:
            #if the value is negative, it means we haven't hit the start time yet
            self.status_flag = 2
        if (time.mktime(time.struct_time(params.end_time))-self.start_time) < 0:
            #if the value is negative, it means we passed the end time
            self.status_flag = 3

    def i2c_pwr(self):
        try:
            # Power on the i2c peripherals via a GPIO
            pwr_i2c = digitalio.DigitalInOut(board.D12)
            pwr_i2c.direction = digitalio.Direction.OUTPUT
            pwr_i2c.value = True
            self.i2c = board.I2C()
        except:
            self.logger.warning('Unable to intiate I2C devices, proceeding without ext RTC or INA')
            print('Unable to intiate I2C devices, proceeding without ext RTC or INA')

    def set_ina(self):
        try:
            self.ina260 = adafruit_ina260.INA260(self.i2c)
        except:
            class ina260():
                voltage = 999
                current = 999
            self.ina260 = ina260()
            self.logger.warning('INA failed, proceeding without voltage measurement')
            print('INA failed, proceeding without voltage measurement')

    def set_clock(self):
        self.rtc_int = rtc.RTC()
        try:
            self.rtc_ext = adafruit_ds3231.DS3231(self.i2c)
            self.rtc_ext_exist = True
            self.rtc_int.datetime = self.rtc_ext.datetime
            flashpixel(self.pixel,5,(0,10,0))
        except:
            self.rtc_ext_exist = False
            self.logger.warning('No External RTC, proceeding')
            flashpixel(self.pixel,5,(0,0,10))
        self.start_time = time.mktime(self.rtc_int.datetime)
        self.start_time_monotonic = math.floor(time.monotonic())
        offset = self.start_time%60
        self.start_time = self.start_time-offset
        self.start_time_monotonic = self.start_time_monotonic-offset

    def mount_sd(self):
        cs = digitalio.DigitalInOut(board.SD_CS)
        sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
        time.sleep(0.1)
        sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, "/sd")

    def initiate_logger(self):
        storage.remount('/',readonly=False)
        self.logger = logging.getLogger(self.params.deployment)
        self.file_handler = FileHandler(self.params.log_file)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)

    def get_file_counter(self):
        try:
            os.stat(self.params.ct_file)
            with open(self.params.ct_file,'r+') as ct_file:
                prev_count  = int(ct_file.read())
                print(prev_count)
                self.file_ct = prev_count+1
                ct_file.seek(0)
                ct_file.write(str(self.file_ct))
            ct_file.close()
        except:
            with open(self.params.ct_file, 'w') as ct_file:
                ct_file.write('0')
            ct_file.close()
            self.file_ct = 0
        

    def setup_ect(self):
        #***Turn on the ECT***
        # Initiate the uart
        self.uart = busio.UART(board.TX, board.RX, baudrate=115200,timeout=.1,receiver_buffer_size=16448)
        # ADD: Power on the ECT by gorunding the MOSFET
        self.pwr_ect = digitalio.DigitalInOut(board.D10) # Set the D10 pin as the grounding pin
        self.pwr_ect.direction = digitalio.Direction.OUTPUT # Set to output
        self.pwr_ect.value = False # Immediately make sure it is off
        time.sleep(1)
        self.pwr_ect.value = True # Turn it on and wait before trying to connect
        time.sleep(2)
        self.logger.info(self.file_datetime+' - C:'+str(self.ina260.current)) # DELETE

        # Check the voltage once the ECT is powered
        if self.ina260.voltage < params.minimum_voltage:
            self.pwr_ect.value = False # immediately depower
            #if the voltage is below what can run the echologger, go back to sleep and try again later
            self.status_flag = 4
        
    def connect_ect(self):
            # If it should have enough juice....
            # Try to connect, which will also make sure we stop it from pinging if it turned on
            if self.pwr_ect.value == False:
                time.sleep(1)
                self.pwr_ect.value = True # Turn it on and wait before trying to connect
                time.sleep(2)
            attempts = 0  
            while attempts <= self.params.max_connect_attempts:
                try:
                    self.ect = echo.Echosounder(self.uart,self.pixel)
                    try:
                        self.ect.Detect()
                    except:
                        self.ect.Detect()
                    self.ect.SetValue("IdTime",str(int(time.mktime(self.rtc_int.datetime))))
                    self.status_flag = 0
                    return 1
                except:
                    self.status_flag = -1
                    
            self.pwr_ect.value = False
            return -1

    def run_ect(self):
        self.get_file_counter()
        # Collect the data files
        for k in self.params.config.keys(): # for each configuration
            # iterate through the config settings and set the values
            for item in self.params.config[k].items(): 
                self.ect.SetValue(item[0],item[1])
                time.sleep(0.05)
            
            # Assign the basename to use for all files with the same configuration
            file_basename = '/sd/'+self.params.deployment+'_'+self.file_datetime+'_'+k+'_'+str(self.file_ct)

            # Dump out the 'info' into a text file
            self.ect.recordInfo(file_basename+'.txt')
            
            # record
            self.ect.recordPings(file_basename+'.bin',numPings=self.params.numPings[k], maxTime=self.params.maxTime[k])

        # Turn the power back off
        self.pwr_ect.value = False

        # If we made it all the way to the end without issue...
        self.status_flag = 1
        
    def to_sleep(self):
        
        sleep_msg = {1:' Successful wakeup, going to sleep',
                    -1:' Unsuccessful wakeup, going to sleep',
                    2:' Wake up earlier than mission start, skipping cycle and going to sleep',
                    3:' Wake up after mission end, going to sleep and deinitializing alarm',
                    4:' Voltage below ECT minimum, skipping cycle and going to sleep',
                    5:' SD card failed to mount'}
        
        dt = _format_datetime(self.rtc_int.datetime)
        to_log = dt+sleep_msg[self.status_flag]
        print(to_log)
        
        if self.status_flag ==1:
            self.logger.info(to_log)
        else:
            self.logger.warning(to_log)
        self.file_handler.close()
        
        # go to sleep
        if self.status_flag == 1:
            flashpixel(self.pixel,3,(0,10,0))
        elif self.status_flag == -1:
            flashpixel(self.pixel,3,(10,0,0))
        else:
           flashpixel(self.pixel,3,(10,10,0))
            
        self.pixel.brightness = 0
        if self.status_flag == 3:
            pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True) # use a pin that it will never be used
            alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
        else:
            time_alarm = alarm.time.TimeAlarm(monotonic_time = self.start_time_monotonic+(self.params.wakeup_interval*60))
            alarm.exit_and_deep_sleep_until_alarms(time_alarm)
            # check if wakeup is later than now or less than some buffer, add interval until it's more than buffer

# Format the datetime for the file basename
def _format_datetime(datetime):
    return "D{:02}{:02}{}T{:02}{:02}{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

def flashpixel(pixel, nTimes, color):
    pixel[0] = (0,0,0)
    time.sleep(0.25)
    for i in range(nTimes):
        pixel[0] = color
        time.sleep(0.25)
        pixel[0] = (0,0,0)
        time.sleep(0.25)