'''
Run and record voltage via an ina260. Used to estimate temperature differences in capacity.

'''
import time
import os
import board
import busio
import neopixel
import digitalio
import storage
import adafruit_sdcard
import echosounder as echo
import adafruit_ina260
import adafruit_ds3231
import rtc

def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )

pixels = neopixel.NeoPixel(board.NEOPIXEL, 1,brightness = .5)
pixels[0] = (10, 10, 0)

# Power the i2c devices, ina260 and ds3231
pwr_i2c = digitalio.DigitalInOut(board.D12)
pwr_i2c.direction = digitalio.Direction.OUTPUT
pwr_i2c.value = True

# establish i2c
i2c = board.I2C()

# connect to rtc and get time
rtc_ext = adafruit_ds3231.DS3231(i2c)
rtc_int = rtc.RTC()
rtc_int = rtc_ext
print(_format_datetime(rtc_int.datetime))

# Connect to ina and get voltage
ina260 = adafruit_ina260.INA260(i2c)
print(ina260.current, ina260.voltage, ina260.power)

# Mount the SD card file system
cs = digitalio.DigitalInOut(board.SD_CS)
sd_spi = busio.SPI(board.SD_CLK, board.SD_MOSI, board.SD_MISO)
sdcard = adafruit_sdcard.SDCard(sd_spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")
pixels[0] = (0, 10, 0)

while ina260.voltage > 3.5:
    pixels[0] = (10, 10, 0)
    time.sleep(2)
    f = open("/sd/batteryRunDown.txt", "a")
    data = _format_datetime(rtc_int.datetime)+' '+','.join([str(a) for a in (ina260.current, ina260.voltage, ina260.power)])+'\n'
    print(data)
    f.write(data)
    f.close()
    pixels[0] = (0, 10, 0)
    time.sleep(2)

pixels[0] = (10, 0, 0)
