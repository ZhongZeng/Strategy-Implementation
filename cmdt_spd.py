# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 18:37:07 2017

@author: Zhong Zeng
"""
import quandl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Fetch Data
# crude oil, unleaded gasoline, heating oil, Pandas DataFrame
co=quandl.get("CHRIS/CME_CL1", authtoken="cartykDByu9tebKyKz2W")
ug=quandl.get("CHRIS/CME_RB1", authtoken="cartykDByu9tebKyKz2W")
ho=quandl.get("CHRIS/CME_HO1", authtoken="cartykDByu9tebKyKz2W")

cop=co["Last"]
ugp=ug["Last"]
hop=ho["Last"]

# Set coefficient
lookback=250 # days of historical lookback 
lam=0.75 # lambda - entry signal
sig=0.25 # sigma - exit signal
pst=0 # current position
riskfree=0.01 # riskfree rate

# Implement Strategy

spd=cop-ugp*2/3*42-hop*42/3
spd=spd.dropna()
pstl=[0] # the list of positions at the begining of the day

for i in range(lookback, spd.size):
    spdi=spd[i-lookback:i]    
    
    if(pstl[-1]==0):
        ubi=spdi.mean()+spdi.std()*lam # upper bound for entry
        lbi=spdi.mean()-spdi.std()*lam # lower bound for entry
        if(spd[i]<lbi):
            pstl.append(1)
        elif(ubi<spd[i]):
            pstl.append(-1)
        else:
            pstl.append(0)
    else:
        ubo=spdi.mean()+spdi.std()*sig # upper bound for exiting
        lbo=spdi.mean()-spdi.std()*sig # lower bound for exiting        
        if(spd[i]<ubo and lbo<spd[i]):
            pstl.append(0)
        else:
            pstl.append(pstl[-1])

# Now we have a list of positions pstl
hldl=[] # the list of portfolio value
pnl0=[] # the list of profit and loss
pnl0dt=[] # the list of date of profit and loss
pnl=[] # the list of profit and loss excluding zero returns
pnldt=[] # the list of date of profit and loss
for i in range(lookback, spd.size):
    hldl.append(spd[i]*pstl[i-lookback])
    if(pstl[i-lookback-1]!=0 and pstl[i-lookback]!=0):
        pnl0.append(spd[i]*pstl[i-lookback]/spd[i-1]/pstl[i-lookback-1]-1)
        pnl0dt.append(spd.index[i])
        pnl.append(spd[i]*pstl[i-lookback]/spd[i-1]/pstl[i-lookback-1]-1)
        pnldt.append(spd.index[i])
    else:
        pnl0.append(0)
        pnl0dt.append(spd.index[i])

# Evaluation Part
# Return, Standard Deviation, and Sharp Ratio
rts0=np.mean(pnl0)*250 # return of the strategy
stds0=np.std(pnl0)*250**0.5 # standard deviation of the strategy
spr0=(rts0-riskfree)/stds0

rts=np.mean(pnl)*250 # return of the strategy
stds=np.std(pnl)*250**0.5 # standard deviation of the strategy
spr=(rts-riskfree)/stds

# Value at Risk, and CVaR
var5=np.percentile(pnl, 5)
var10=np.percentile(pnl, 10)
cvar5=np.mean([num for num in pnl if num<var5])
cvar10=np.mean([num for num in pnl if num<var10])

# Return Distribution
plt.xlabel('Returns')
plt.ylabel('Observations')
plt.title('Return Distribution')
pnln, pnlbins, pnlpatches = \
    plt.hist([num for num in pnl if num<1 and -1<num], 100)       
plt.show()

# PnL Time Series
plt.xlabel('Time Horizon')
plt.ylabel('Return')
plt.title('PnL Time Serise Graph')
plt.plot(pnl0dt, pnl0)
plt.show()
        
