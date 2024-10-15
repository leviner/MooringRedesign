import time
import os
import board
import busio
import neopixel
import digitalio
import rtc
import storage
import alarm

import adafruit_sdcard
import adafruit_ina260
import adafruit_ds3231
import adafruit_logging as logging
from adafruit_logging import FileHandler

import echosounder as echo
from params import params

class rp2040_logger():
    def __init__(self,params):
        self.wakeup_flag = 0
        self.pixel = neopixel.NeoPixel(board.NEOPIXEL, 1,brightness = .5)
        self.pixel[0] = (0,0,10)
        self.params = params
        self.i2c_pwr()
        time.sleep(.05)
        self.set_clock()
        
        self.file_datetime = _format_datetime(self.rtc_int.datetime)
        self.mount_sd()
        self.ina260 = adafruit_ina260.INA260(self.i2c)
        self.initiate_logger()

        # First check that we woke up during the time we're supposed to be collecting data
        if (time.mktime(self.rtc_int.datetime)-time.mktime(time.struct_time(self.params.start_time))) < 0:
            #if the value is negative, it means we haven't hit the start time yet
            self.wakeup_flag = 2
        if (time.mktime(time.struct_time(params.end_time))-time.mktime(self.rtc_int.datetime)) < 0:
            #if the value is negative, it means we passed the end time
            self.wakeup_flag = 3
        print(self.rtc_int.datetime)

    def i2c_pwr(self):
        # Power on the i2c peripherals via a GPIO
        pwr_i2c = digitalio.DigitalInOut(board.D12)
        pwr_i2c.direction = digitalio.Direction.OUTPUT
        pwr_i2c.value = True
        self.i2c = board.I2C()

    def set_clock(self):
        self.rtc_ext = adafruit_ds3231.DS3231(self.i2c)
        self.rtc_int = rtc.RTC()
        self.rtc_int.datetime = self.rtc_ext.datetime
        #alarm_time = time.struct_time((0,0,0,0,0,0,0,0,0))
        alarm_time = time.struct_time((0,0,0,0,(self.rtc_int.datetime.tm_min+2)%60,0,0,0,0)) # this is a test for 5 minute cycles
        self.rtc_ext.alarm1 = (alarm_time,'hourly') # this is a test for 
        #self.rtc_ext.alarm1 = (alarm_time,'minutely')
        self.rtc_ext.alarm1_status = False # reset the alarm

    def mount_sd(self):
        cs = digitalio.DigitalInOut(board.SD_CS)
        sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
        time.sleep(0.1)
        sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
        vfs = storage.VfsFat(sdcard)
        storage.mount(vfs, "/sd")

    def initiate_logger(self):
        self.logger = logging.getLogger(self.params.deployment)
        self.file_handler = FileHandler(self.params.log_file)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info(self.file_datetime+' - Awake, V:'+str(self.ina260.voltage))
        self.logger.info(self.file_datetime+' - C:'+str(self.ina260.current)) # DELETE
        

    def get_file_counter(self):
        # Check for the number of binary files we've already written and iterate the counter
        files = os.listdir('/sd')
        # the counter is the number of files, divided by the number of configs
        self.file_ct = int(sum(['.bin' in f for f in files])/len(self.params.config)) 

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
            self.wakeup_flag = 4
            print('low voltage')
        
    def connect_ect(self):
            # If it should have enough juice....
            # Try to connect, which will also make sure we stop it from pinging if it turned on
            if self.pwr_ect.value == False:
                time.sleep(1)
                self.pwr_ect.value = True # Turn it on and wait before trying to connect
                time.sleep(2)
                
            try:
                self.ect = echo.Echosounder(self.uart,self.pixel)
                try:
                    self.ect.Detect()
                except:
                    self.ect.Detect()
                self.ect.SetValue("IdTime",str(int(time.mktime(self.rtc_int.datetime))))
                self.wakeup_flag = 0
                return 1
            except:
                self.wakeup_flag = -1
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

        # Check that there's a new .bin file that contains the file_basename date in it
        files = os.listdir('/sd') # scan the sd card again
        if (sum([file_basename in f for f in files])) > 1: # there should be at least 2
            self.wakeup_flag = -1

        # If we made it all the way to the end without issue...
        self.wakeup_flag = 1
        
    def to_sleep(self):
        
        if self.wakeup_flag == 1:
            msg = ' Successful wakeup, going to sleep'
        elif self.wakeup_flag == -1:
            msg = ' Unsuccessful wakeup, going to sleep'
        elif self.wakeup_flag == 2:
            msg = ' Wake up earlier than mission start, skipping cycle and going to sleep'
        elif self.wakeup_flag == 3:
            msg = ' Wake up after mission end, going to sleep and deinitializing alarm'
        elif self.wakeup_flag == 4:
            msg = ' Voltage below ECT minimum, skipping cycle and going to sleep'
        
        dt = _format_datetime(self.rtc_int.datetime)
        to_log = dt+msg
        print(to_log)
        
        if self.wakeup_flag ==1:
            self.logger.info(to_log)
        else:
            self.logger.warning(to_log)
        self.file_handler.close()
        
        # go to sleep
        if self.wakeup_flag == 3:
            self.rtc_ext.alarm1_status = True
            pin_alarm = alarm.pin.PinAlarm(pin=board.D11, value=False, pull=True) # use a pin that it will never read
            alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
            rp.pixel.brightness = 0
        else:
            pin_alarm = alarm.pin.PinAlarm(pin=board.D9, value=False, pull=True)
            self.pixel[0] = (0,10,0)
            time.sleep(1)
            alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
            rp.pixel.brightness = 0

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