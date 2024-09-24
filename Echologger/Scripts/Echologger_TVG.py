# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 15:56:56 2024

@author: alex.derobertis
"""

# import libraries
import numpy as np
import matplotlib.pyplot as plt


# functions
# define echologger TVG function as I understand it
# function to compute TVG function as f(range)
def TVG(r,gain_zero,gain_sel,alpha,K,min_gain,max_TVG_gain,r_spread):
    # function to simulate Echologger TVG function
    # 1) if gain(r)< min gain, then gain =min_gain
    # 2) if range is <= r_spread, gain = gain_sel +  k*10*log10(2*r) +(alpha*2*r)
    # 3 if range > r_spread, gain only increases by absorption from this range
    
    spreading = K*np.log10(r*2)  # spreading applied on 2x range ** confirmed iwth manufacturer ***
    absorption = (alpha*r*2)
    
    
    fTVG = gain_zero + gain_sel+ absorption  # apply TVG without spreading
    fTVG[r<=r_spread]=fTVG[r<=r_spread] + spreading[r<=r_spread] #add TVG for spreading for r<= r_spread
    fTVG[r>r_spread]=fTVG[r>r_spread] + max(spreading[r<=r_spread]) # add max spreading TVG to rest of obs (i.e. applied but not increasing)
    
    
    ind=fTVG<min_gain # now apply min gain
    fTVG[ind]=min_gain
    
    ind=fTVG>min_gain+max_TVG_gain # now apply min gain
    fTVG[ind]=min_gain+max_TVG_gain
    
    return fTVG
    



#%% paramters for the run
r=np.arange(1,200)
#gain_zero=20 # 30 dB 'zero gain' for 30 kHz, 20 for 200 kHz
gain_sel=6 # set to zero dB
alpha=0.05 # absorption coefficient in dB per m
min_gain=50 # from PDF supplied by echologger
K=15 # standard TVG coeff

# freuency-specific paramters
max_TVG_gain_200=45
max_TVG_gain_30=35
r_spread_200=50 # max range for which spreading is applied in TVG [m]
r_spread_30=100 # max range for which spreading is applied in TVG [m]



TVG_200=TVG(r,30,gain_sel,alpha,K,min_gain,max_TVG_gain_200,r_spread_200)
TVG_30=TVG(r,20,gain_sel,alpha,K,min_gain,max_TVG_gain_30,r_spread_30)

# add a quickplot

fig=plt.figure() # inititate figure
plt.plot(r,TVG_200,label='200 Khz')
plt.plot(r,TVG_30,label='38 Khz')

plt.xlabel('Range (m)')
plt.ylabel('Total Gain applied (dB)')
plt.ylim(48,120)

plt.grid()  
plt.title("Echologger TVG function: K=" + str(K) + ' Gain='+ str(gain_sel) +
          ' alpha=' + str(alpha) + ' r_spread=' + str(r_spread) + ' max TVG = '+str(max_TVG_gain_200) +'/'+str(max_TVG_gain_30)) 
plt.legend() 