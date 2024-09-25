'''
Class for reading echosounder files from the Echologger.

Example usage:
****
import echologgerData as echo
data = echo.echologgerData()
data.readTextFile(FILE)

data = echo.echologgerData()
data.readBinaryFile(FILE)
****

Two plotting functions:
    - data.echogram: plots an echogram (default in log)
    - data.plotPing: plots a ping, an average of set of pings, 
        or an average of all pings in a file, as specified by 
        pingIdx value

'''

import re
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import struct
import xarray as xr

class echologgerData():
    def __init__(self):
        pass

    def resetArray(self):
        '''
        Everytime we read a new file, everything gets reset
        '''
        self.allPings = []
        self.Time = []
        self.pingNo = []
        self.gain = []
        self.pitch = []
        self.roll = []
        self.alt = []
        self.range = []
        self.temp = []
        self.frequency = []
        self.fileFmt = None

    def readTextFile(self,file):
        '''
        Parse the Echo 12-bit text file format
        '''
        self.resetArray() # Setup the holding variables

        # Read through by line, pull header info
        with open(file, 'r') as f:
            for line in f:
                if '#Range,m' in line:
                    fileRange = float(re.findall("\d+\.\d+", line)[0])
                if '#NSamples' in line:
                    nSamples = int(re.findall("\d+", line)[0])
                    self.range.append(np.linspace(0,fileRange, nSamples))
                if '#TimeWork' in line:
                    self.Time.append(datetime.fromtimestamp(float(re.findall("\d+\.\d+", line)[0])))
                if '#Ping ' in line:
                    self.pingNo.append(int(re.findall("\d+", line)[0]))
                if '#TVG_Gain' in line:
                    self.gain.append(float(re.findall("[+-]?\d+\.\d+", line)[0]))
                if '#Pitch,deg' in line:
                    self.pitch.append(float(re.findall("[+-]?\d+\.\d+", line)[0]))
                if '#Roll,deg' in line:
                    self.roll.append(float(re.findall("[+-]?\d+\.\d+", line)[0]))
                if '##DataStart' in line:                
                    newPing= []
                    for line in f: # now you are at the lines you want
                        if '##DataEnd' not in line:
                            newPing.append(int(line))
                        else:
                            data.allPings.append(np.asarray(newPing))
                            break

        # change lists to np arrays
        self.allPings = np.asarray(self.allPings)
        self.pingNo = np.asarray(self.pingNo)
        self.range = np.asarray(self.range)
        self.fileFmt = 'txt' # set the file format

    def echogram(self,log=True):
        '''
        Quick and dirty echogram plot
        '''
        fig = plt.figure()
        if log:
            C =np.log10(self.allPings.T)
        else:
            C = self.allPings.T
        
        plt.pcolormesh(self.Time,self.range[0],C)
        plt.gca().invert_yaxis()
        plt.ylabel('Range')
        plt.xlabel('Time')
        plt.colorbar()
        plt.grid(axis='y',linestyle='--')

    def plotPing(self, log=True, pingIdx=None, newFig=True):
        '''
        Plot a single ping, default is in log space
        pingIdx is list of ping numbers, e.g., [1,3,7]
        '''
        if newFig:
            fig = plt.figure()

        if pingIdx is None:
            pltData = np.mean(self.allPings,axis=0)
        else:
            pltData = np.mean(self.allPings[pingIdx],axis=0)
        
        if log:
            pltData = 20*np.log10(pltData)
        
        plt.plot(self.range[0],pltData)
        plt.grid(True)

    def readBinaryFile(self, file):
        '''
        Parse the 8-bit compressed and 12-bit binary Echologger files
        recorded via the API or the microcontroller. Note: this does not parse
        files recorded using the Dual Echosounder .exe provided by Echologger.
        '''

        def parseHeader(data):
            # Inner function for parsing header
            packetLength, utctime, utcms, ping, alt, temp, pitch, roll, fmat, nSamples, samprange, freq, samprate = struct.unpack("I I I I f f f f I I f I I",data)
            pingTime = datetime.fromtimestamp(utctime+(utcms/1000))
            return ping, pingTime, packetLength, temp, alt, pitch, roll, fmat, nSamples, samprange, freq, samprate

        with open(file, "rb") as binary_file:
            # Read the whole file at once
            data = binary_file.read()
            binary_file.close()

        # Setup the holding attributes
        self.resetArray()

        cur_pos = 0 # initial starting position of the file

        magicL = 10 # expected length of magic/id string
        headerL = 52 # expected length of header datagram

        while data[cur_pos:].find(b'ECHOLOGGEC') !=-1:

            # The start of a new ping indicated by the 'magic' string
            newPingStart = data[cur_pos:].find(b'ECHOLOGGEC')+cur_pos

            try:
                magic = data[newPingStart:newPingStart+magicL] # read the magic bytes
                header = data[newPingStart+magicL:headerL+magicL+newPingStart] # read the rest of the header bytes
                
                # Partse the header
                ping, pingTime, packetLength, temp, alt, pitch, roll, fmat, nSamples, sampRange, freq, samprate = parseHeader(header)
                        
                nSamples = packetLength-magicL-headerL # The remaining bytes in the packet are our samples
                samples = data[headerL+magicL+newPingStart:headerL+magicL+newPingStart+nSamples]
                sample_upack = struct.unpack(''.join(["h"] * int(nSamples/2)),samples) # Unpack all remaining bytes as Int16

                # FIll in our holding variables            
                self.allPings.append(np.array(sample_upack))
                self.range.append(np.linspace(0,sampRange, int(nSamples/2)))
                self.Time.append(pingTime)
                self.pingNo.append(ping)
                self.temp.append(temp)
                self.alt.append(alt)
                self.pitch.append(pitch)
                self.roll.append(roll)
                self.frequency.append(freq)
                
                # Move forward to our next ping
                cur_pos+=packetLength
            except:
                # If we fail to read in the ping, by default move forward to the next position
                cur_pos+=packetLength

        # Convert lists to np arrays
        self.allPings, self.range, self.Time, self.pingNo, self.temp, self.alt, self.pitch, self.roll, self.frequency = 
            [np.asarray(x) for x in [self.allPings, self.range, self.Time, self.pingNo, self.temp, self.alt, self.pitch, self.roll, self.frequency]]
        
        # Set the file type
        self.fileFmt = 'bin'

    def toXarray(self):
        ds = xr.Dataset(data_vars=dict(samples=(["time","range"],self.allPings),
                            freq=(["time"],self.frequency),
                            altitude=(["time"],self.alt),
                            pitch=(["time"],self.pitch),
                            roll=(["time"],self.roll)
                            ), 
                coords=dict(time=("time",self.Time), 
                            range=("range",self.range[0]),
                            ),
                            attrs=dict(FileFormat=self.fileFmt))
        return ds