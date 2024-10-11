import time

class Echosounder():
    def __init__(self,uart):
        self._serial_port = uart
        self._is_running = False
        self._is_detected = False
        self._info_lines = []
        self._command_result = ""
        
        self._is_detected = self.Detect()
        if True == self_is_detected():
            self._GetEchosounderInfo()
    
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

            if 1 != self.__SendCommandResponseCheck():
                result = False                
            else:
                self.__WaitCommandPrompt(1000)
                result = True
                self._is_detected = True
            break

        return result
            
    def __WaitCommandPrompt(self, timeoutms):
        """! Waiting until echosounder send back "command prompt" character
        @param timeoutms - timeout in milliseconds
        @result 1 - command prompt received, -2 - timeout occured
        """
        time_begin = time.monotonic_ns()

        while True:
            ch = self._serial_port.read()

            if len(ch) > 0:                
                if ch.decode('latin_1') == '>':
                    return 1

            period = time.monotonic_ns() - time_begin
            if period > timeoutms * 1000000:
                return -2


    def __SendCommandResponseCheck(self):
        """! Echosounder's command's response check
        @result 1 - command successfuly execute, 2 - invalid argument, 3 - invalid command, -2 - timeout occured
        """
        magicidbuffer   = "00000000000000000000"
        invalidargtoken = "Invalid argument\r\n"
        invalidcmdtoken = "Invalid command\r\n"
        okgotoken       = "OK go\r\n"
        oktoken         = "OK\r\n"

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
                    return 1
                if magicidbuffer[-len(oktoken):] == oktoken:
                    self._is_running = False
                    return 1
                if magicidbuffer[-len(invalidargtoken):] == invalidargtoken:
                    self._is_running = False
                    return 2
                if magicidbuffer[-len(invalidcmdtoken):] == invalidcmdtoken:
                    self._is_running = False
                    return 3            

            period = time.monotonic_ns() - time_begin
            if period > 4000000000: # 4s timeout hardcoded
                return -2