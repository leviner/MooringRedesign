import re
import time
import random

class Echosounder():
    def __init__(self,uart,pixels):
        self._serial_port = uart
        self._is_running = False
        self._is_detected = False
        self._info_lines = []
        self._command_result = ""
        self._is_detected = self.Detect()
        self._pixels = pixels
        
        self._sonarcommands = [
    ( "IdInfo",            "#info",       "",      ""),
    ( "IdRange",           "#range",      "50000", " - #range[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*"),
    ( "IdRangeH",          "#rangeh",     "50000", " - #rangeh[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*"),
    ( "IdRangeL",          "#rangel",     "50000", " - #rangel[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*"),
    ( "IdInterval",        "#interval",   "1.0",   " - #interval[ ]{0,}\\[[ ]{0,}(([0-9]*[.])?[0-9]+) sec[ ]{0,}\\].*") ,
    ( "IdPingonce",        "#pingonce",   "0",     " - #pingonce[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdTxLength",        "#txlength",   "50",    " - #txlength[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdTxLengthH",       "#txlengthh",  "50",    " - #txlengthh[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdTxLengthL",       "#txlengthl",  "100",   " - #txlengthl[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdTxPower",         "#txpower",    "0.0",   " - #txpower[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB[ ]{0,}\\].*" ),
    ( "IdGain",            "#gain",       "0.0",   " - #gain[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB[ ]{0,}\\].*" ),
    ( "IdGainH",           "#gainh",      "0.0",   " - #gainh[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB[ ]{0,}\\].*" ),
    ( "IdGainL",           "#gainl",      "0.0",   " - #gainl[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB[ ]{0,}\\].*" ),
    ( "IdTVGMode",         "#tvgmode",    "1",     " - #tvgmode[ ]{0,}\\[[ ]{0,}([0-4]{1})[ ]{0,}\\].*" ),
    ( "IdTVGAbs",          "#tvgabs",     "0.140", " - #tvgabs[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB\\/m[ ]{0,}\\].*" ),
    ( "IdTVGAbsH",         "#tvgabsh",    "0.140", " - #tvgabsh[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB\\/m[ ]{0,}\\].*" ),
    ( "IdTVGAbsL",         "#tvgabsl",    "0.060", " - #tvgabsl[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) dB\\/m[ ]{0,}\\].*" ),
    ( "IdTVGSprd",         "#tvgsprd",    "15.0",  " - #tvgsprd[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+)[ ]{0,}\\].*" ),
    ( "IdTVGSprdH",        "#tvgsprdh",   "15.0",  " - #tvgsprdh[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+)[ ]{0,}\\].*" ),
    ( "IdTVGSprdL",        "#tvgsprdl",   "15.0",  " - #tvgsprdl[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+)[ ]{0,}\\].*" ),
    ( "IdAttn",            "#attn",       "0",     " - #attn[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdAttnH",           "#attnh",      "0",     " - #attnh[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdAttnL",           "#attnl",      "0",     " - #attnl[ ]{0,}\\[[ ]{0,}([0-9]{1,}) uks[ ]{0,}\\].*" ),
    ( "IdSound",           "#sound",      "1500",  " - #sound[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mps[ ]{0,}\\].*" ),
    ( "IdDeadzone",        "#deadzone",   "300",   " - #deadzone[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdDeadzoneH",       "#deadzoneh",  "300",   " - #deadzoneh[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdDeadzoneL",       "#deadzonel",  "500",   " - #deadzonel[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdThreshold",       "#threshold",  "10",    " - #threshold[ ]{0,}\\[[ ]{0,}([0-9]{1,}) %[ ]{0,}\\].*" ),
    ( "IdThresholdH",      "#thresholdh", "10",    " - #thresholdh[ ]{0,}\\[[ ]{0,}([0-9]{1,}) %[ ]{0,}\\].*" ),
    ( "IdThresholdL",      "#thresholdl", "10",    " - #thresholdl[ ]{0,}\\[[ ]{0,}([0-9]{1,}) %[ ]{0,}\\].*" ),
    ( "IdOffset",          "#offset",     "0",     " - #offset[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdOffsetH",         "#offseth",    "0",     " - #offseth[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdOffsetL",         "#offsetl",    "0",     " - #offsetl[ ]{0,}\\[[ ]{0,}([0-9]{1,}) mm[ ]{0,}\\].*" ),
    ( "IdMedianFlt",       "#medianflt",  "2",     " - #medianflt[ ]{0,}\\[[ ]{0,}([0-9]{1,3})[ ]{0,}\\].*" ),
    ( "IdSMAFlt",          "#movavgflt",  "1",     " - #movavgflt[ ]{0,}\\[[ ]{0,}([0-9]{1,3})[ ]{0,}\\].*" ),
    ( "IdNMEADBT",         "#nmeadbt",    "1",     " - #nmeadbt[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdNMEADPT",         "#nmeadpt",    "0",     " - #nmeadpt[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdNMEAMTW",         "#nmeamtw",    "1",     " - #nmeamtw[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdNMEAXDR",         "#nmeaxdr",    "1",     " - #nmeaxdr[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdNMEAEMA",         "#nmeaema",    "0",     " - #nmeaema[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdNMEAZDA",         "#nmeazda",    "0",     " - #nmeazda[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdOutrate",         "#outrate",    "0.0",   " - #nmearate[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) sec[ ]{0,}\\].*" ),
    ( "IdNMEADPTOffset",   "#nmeadptoff", "0.0",   " - #nmeadptoff[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) m[ ]{0,}\\].*" ),
    ( "IdNMEADPTZero",     "#nmeadpzero", "1",     " - #nmeadpzero[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdOutput",          "#output",     "3",     " - #output[ ]{0,}\\[[ ]{0,}([0-9]{1,})[ ]{0,}\\].*" ),
    ( "IdAltprec",         "#altprec",    "3",     " - #altprec[ ]{0,}\\[[ ]{0,}([1-4]{1})[ ]{0,}\\].*" ),
    ( "IdSamplFreq",       "#samplfreq",  "0",     " - #samplfreq[ ]{0,}\\[[ ]{0,}([0-9]{1,6})[ ]{0,}\\].*" ),
    ( "IdTime",            "#time",       "0",     " - #time[ ]{0,}\\[[ ]{0,}([0-9]{1,})[ ]{0,}\\].*" ),
    ( "IdSyncExtern",      "#syncextern", "0",     " - #syncextern[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdSyncExternMode",  "#syncextmod", "1",     " - #syncextmod[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdSyncOutPolarity", "#syncoutpol", "1",     " - #syncoutpol[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdAnlgMode",        "#anlgmode",   "0",     " - #anlgmode[ ]{0,}\\[[ ]{0,}([01]{1})[ ]{0,}\\].*" ),
    ( "IdAnlgRate",        "#anlgrate",   "0.100", " - #anlgrate[ ]{0,}\\[[ ]{0,}([+-]?([0-9]*[.])?[0-9]+) V\/m[ ]{0,}\\].*" ),
    ( "IdAnlgMaxOut",      "#anlgmax",    "4",     " - #anlgmax[ ]{0,}\\[[ ]{0,}([1-4]{1})[ ]{0,}\\].*" ),
    ( "IdVersion",         "#version",    "",      " S\\/W Ver: ([0-9]{1,}[.][0-9]{1,}) .*" ),

    ( "IdSetHighFreq",     "#setfh",      "",      "" ),
    ( "IdSetLowFreq",      "#setfl",      "",      "" ),
    ( "IdSetDualFreq",     "#setfd",      "",      "" ),

    ( "IdGetHighFreq",     "#getfh",      "",      ".*High Frequency:[ ]{0,}([0-9]{4,})Hz.*" ),
    ( "IdGetLowFreq",      "#getfl",      "",      ".*Low Frequency:[ ]{0,}([0-9]{4,})Hz.*" ),
    ( "IdGetWorkFreq",     "#getf",       "",      ".*:[ ]{1,}([0-9]{4,})Hz[ ]{0,}\\(Active\\).*" ),

    ( "IdGo",              "#go",         "",      "" )]
        
    def Detect(self):
        result = False
        self._is_detected = False
        for i in range(0, 10):
            self._serial_port.write(bytes('\r', 'latin_1'))
            time.sleep(0.05)
            self._serial_port.write(bytes('\r', 'latin_1'))
            time.sleep(0.05)
            self._serial_port.write(bytes('\r', 'latin_1'))
            time.sleep(0.05)            
            self._serial_port.write(bytes('\r', 'latin_1'))
            time.sleep(0.05)            
            self._serial_port.write(bytes('\r', 'latin_1'))
            time.sleep(0.05)
            
            if 1 == self.__WaitCommandPrompt(500):
                self._serial_port.write(bytes("#speed\r", 'latin_1'))
                time.sleep(0.05)

                if 1 != self.__SendCommandResponseCheck():
                    result = False
                    print('tried')
                else:
                    self.__WaitCommandPrompt(1000)
                    result = True
                    self._is_detected = True
                break

        return result
    
    def __WaitCommandPrompt(self, timeoutms):
        time_begin = time.monotonic_ns()
        self._serial_port.write(bytes('\r', 'latin_1'))

        while True:
            ch = self._serial_port.read()
           
            if len(ch) > 0:                
                if ch.decode('latin_1')[-1] == '>':
                    return 1

            period = time.monotonic_ns() - time_begin
            if period > timeoutms * 1000000:
                return -2
        
            
    def __SendCommandResponseCheck(self):
        magicidbuffer   = "00000000000000000000"
        invalidargtoken = "Invalid argument\r\n"
        invalidcmdtoken = "Invalid command\r\n"
        okgotoken       = "OK go\r\n"
        oktoken         = "OK\r\n\r\n"

        self._command_result = ""
        time_begin = time.monotonic_ns()

        while True:
            ch = self._serial_port.read()

            if len(ch) > 0:                
                magicidbuffer = magicidbuffer[1:]
                chs = ch.decode('latin_1')

                magicidbuffer = magicidbuffer + chs
                self._command_result = self._command_result + chs

                if magicidbuffer[-len(okgotoken):] == okgotoken:
                    self._is_running = True
                    print(1)
                    return 1
                if oktoken in magicidbuffer:
                    self._is_running = False
                    print(2)
                    return 1
                if magicidbuffer[-len(invalidargtoken):] == invalidargtoken:
                    self._is_running = False
                    print(3)
                    return 2
                if magicidbuffer[-len(invalidcmdtoken):] == invalidcmdtoken:
                    self._is_running = False
                    print(4)
                    return 3     
            
            period = time.monotonic_ns() - time_begin
            if period > 4000000000: # 4s timeout hardcoded
                return -2
    
    def Stop(self):
        return self.Detect()

    def SendCommand(self, Command):
        result = -1
        wasrunning = self._is_running

        if True == self._is_running:
            self.Stop()

        for command in self._sonarcommands:
            if command[0] == Command:
                fullcommand = command[1] + '\r'
                self._serial_port.write(bytes(fullcommand, 'latin_1'))
                result = self.__SendCommandResponseCheck()
                time.sleep(0.05)
                self.__WaitCommandPrompt(1000)

        if True == wasrunning:
            self.Start()

        return result
    

    def __GetEchosounderInfo(self):
        self._info_lines = []
        result = self.SendCommand("IdInfo")

        if 1 == result:
            self._info_lines = self._command_result.splitlines()
            for line in self._info_lines:
                line.replace("\r", "").replace("\n", "")
                
    
    def SetValue(self, Command, Value):
        retvalue = False
        wasrunning = self._is_running

        if True == self._is_running:
            self.Stop()

        for command in self._sonarcommands:
            if command[0] == Command and len(command[2]) > 0:
                fullcommand = command[1] + ' ' + Value  + '\r'
                self._serial_port.write(bytes(fullcommand, 'latin_1'))

                retvalue = True if (1 == self.__SendCommandResponseCheck()) else False

                self.__WaitCommandPrompt(1000)
                break
        
        if True == wasrunning:
            self.Start()

        return retvalue
    
    def Start(self):
        self._serial_port.write('#go\r\n')
        time.sleep(0.05)
        self._serial_port.read()
        self._is_running = True
    
    def recordPings(self, outputFile, numPings=10, maxTime=10):
        time_begin = time.time()
        self._pixels[0] = (10, 10, 0)
    
        with open(outputFile, "wb") as binary_file:
            ping = 0
            self._serial_port.write('#go\r\n')
            time.sleep(0.05)
            self._serial_port.read() # clear the buffer
            time.sleep(1) # wait for the pinging to start
            while (ping <numPings) & (time.time() < time_begin+maxTime): 
                # Read the stream
                input = self._serial_port.read()
                if input:
                    binary_file.write(input)
                    if b'ECHOLOGG' in input:
                        ping+=1
                        self._pixels[0] = (random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
                        print('Echo detected, ping ',ping)
                        
                        
            try:
                self.Detect()
            except:
                self.Detect()

        while self._is_running: 
            # Run a detect to stop pinging
            try:
                self.Detect()
            except:
                self.Detect()
            
        binary_file.close()
    
    def recordInfo(self,outputFile):
        self.__GetEchosounderInfo()
            
        with open(outputFile,'w') as file:
            for line in self._info_lines:
                if len(line) > 0:
                    file.write(line+'\r')
        file.close()