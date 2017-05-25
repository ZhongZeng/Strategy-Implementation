# -*- coding: utf-8 -*-
"""
Created on Fri Apr 21 11:19:28 2017

@author: Zhong Zeng
"""

import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

def aDate(sdata, yr2, mth2, dt2):
    # return the dataframe of stocks at a specified date
    # Input variable: data, year, month, date
    # Type: dataframe, int, int, int
    date2 = yr2*1e4+mth*1e2+dt2
    #yr2 = int( date2 / 1e4)
    #dt2 = int( date2 % 1e2)
    #mth2 = int (( date2 % 1e4) /1e2)
    while True:        
        date2 = yr2*1e4+mth*1e2+dt2
        sd2=sdata[sdata['datadate']==date2]
        if(sd2.empty==False):
            break
        if(dt2<31):
            dt2=dt2+1 # move to the following calendar day
        else: 
            dt2=1
            if(mth2<12):
                mth2=mth2+1 # move to the following calendar month
            else:
                mth2=1
                yr2=yr2+1 # move to the following calendar year    
    return [int(date2), sd2]

def formPort( sdata, adds, buy, weighting):
    # Select certain stocks to formulate a equally weighted portfolio
    # Input variable: data, list of stocks to be added/deleted, 1/-1 for buy/sell
    # Type: dataframe, dataframe, 1/-1
    if (weighting=='equal'):
        w='prccd'
    elif(weighting=='mktcp'):
        w='cshoc'
    
    sdata_add=sdata[bd-1<sdata['datadate']][sdata['datadate']<ed][sdata['cusip'].isin(adds['cusip'])]    
    sdata_add.interpolate(method='linear', limit_direction='forward') # Interpolate Data
    # form a dataframe of holding # of shares
    sdata_add_h = sdata_add[sdata_add['datadate']==bd][[w,'cusip']]
    sdata_add_h = sdata_add_h.rename(columns = {w:'h'})
    
    if (weighting=='equal'):
        sdata_add_h['h'] = buy * 1e4 / sdata_add_h['h']
    elif(weighting=='mktcp'):
        sdata_add_h['h'] = sdata_add_h['h'] # / 1e4
        
    # the holding number of shares; join doesn't work
    sdata_add = pd.merge(sdata_add, sdata_add_h, on='cusip', how='outer')
    # holiding values
    sdata_add['prt'] = sdata_add['prccd']*sdata_add['h'] 
    return sdata_add

def eva(rt_s):
    # return evaluate matrics
    # Input variable: list of return
    # Type: list of float
    riskfree=0.02
    # Return, Standard Deviation, and Sharp Ratio
    rts=np.mean(rt_s)*250 # annulized return of the strategy
    stds=np.std(rt_s)*250**0.5 # annulized standard deviation of the strategy
    spr=(rts-riskfree)/stds
    
    # Value at Risk, and CVaR
    var5=np.percentile(rt_s, 5)
    var10=np.percentile(rt_s, 10)
    cvar5=np.mean([num for num in rt_s if num<var5])
    cvar10=np.mean([num for num in rt_s if num<var10])
    return [rts, stds, spr, var5, var10, cvar5, cvar10]
  
def plotReturn(rt_s, yr2, bins, cum):
    # Return Distribution
    # Input variable: list of return, year, #bins, is cumulative or not
    # Type: list of float, int, int, str
    plt.xlabel('Returns')
    plt.ylabel('Observations')
    plt.title(cum+' Return Distribution of Year '+str(yr2))
    pnln, pnlbins, pnlpatches = plt.hist(rt_s, bins)        
    # add a 'best fit' normal distributed line
    y = mlab.normpdf( pnlbins, np.mean(rt_s), np.std(rt_s))*(pnlbins[1]-pnlbins[0])*len(rt_s)
    l = plt.plot(pnlbins, y, 'r--', linewidth=1)
    plt.show()
    
    # PnL Time Series
    plt.xlabel( 'Time Horizon')
    plt.ylabel( 'Return')
    plt.title( cum+' PnL Time Serise Graph of Year '+str(yr2))
    plt.plot( rt_s) # [str(int(dti%1e4)) for dti in dt_s],
    # plt.plot([dti%1e4-630 for dti in dt_s], rt_s) # 0 on x-axis is the day of actual rebalance
    plt.show()
              
#"""
# Set path of the csv file
path = 'F:\Michael\Fordham_University\Alternative_Investment\Idx_Rb\Data\\'
sfile = 'data3.csv' # stock data from WRDS

# Col Names: gvkey iid	datadate	cusip	cshoc	prccd	conml	loc
# Used Col: datedate(int) cusip(int) cshoc(float64) prccd(float64)
sdata = pd.read_csv( path + sfile, usecols=['datadate', 'cusip', 'cshoc', 'prccd']) 
print('csv data file read' + '\n')

# Add year
sdata['year']=sdata['datadate']/1e4
sdata['year']=sdata['year'].astype(int)
print('year added' + '\n')

# Add and Calculate Market Capitalization (float64)
sdata['mktcap']=sdata['cshoc']*sdata['prccd']
print('Mkt Cap calculated' + '\n')

# Add Rank (float64) by Market Cap ('mktcap') group by 'date' 
sdata['rnk']=sdata.groupby('datadate')['mktcap'].rank(ascending=False)
print('Rank added' + '\n')

#-------------Done w/ Reading Files and Data Input-------------------#
#"""
#------------------------------Input Variables-----------------------#
yrb=2006 # the beginning year
yre=2016 # the ending year
mth = 5 # month of entering
dt = 20 # date of entering
mth_r = 5 # month of reconsititution calculation
dt_r = 31 # date of reconsititution calculation
rnk_lb = 1000 # lower bond of the rank
rnk_ub = 3000 # upper bond of the rank
# bd = 80 # entering/begining date
mth_e = 7 # exiting month
dt_e = 10 # exiting date
print('Input variables added' + '\n')

#-------------Initialize Lists of Evaluation Matrix-----------------#
ls_to=[] # list of turn over rate
ls_add_rt=[] # list of added stock returns
ls_del_rt=[] # list of deleteded stock returns
ls_add_n=[] # list of number of added stocks
ls_del_n=[] # list of number of deleted stocks

ls_prt_rt=[] # list of lists of portfolio's returns yearly
rt_s_all=[] # list of portfolio's returns in total
rt_c_all=[] # list of portfolio's cumulative returns in total

Avg_Return=[] # list of portfolio's returns
Std_Dev=[] # list of portfolio's volatility(Standard Deviation)
Sharp_Ratio=[] # list of portfolio's Sharp ratio
VaR_5prct=[] # list of portfolio's 5% VaR
VaR_10prct=[] # list of portfolio's 10% VaR 
CVaR_5prct=[] # list of portfolio's 5% CVaR
CVaR_10prct=[] # list of portfolio's 10% CVaR

#----------------Implement and Evaluate Strategy-------------#
for yri in range(yrb, yre): # yrb+2
    # Rank stocks and choose them by market cap    
    yr1 = yri
    mth1 = mth_r
    dt1 = dt_r
    [rd, sd1] = aDate(sdata, yr1, mth1, dt1) # rd is the eintering date of last year
    
    yr2 = yri+1
    mth2 = mth
    dt2 = dt
    [bd, sd2] = aDate(sdata, yr2, mth2, dt2) # bd is the begining/entering date
    
    # Find the stocks to add or delete 
    sd1rsl = sd1[sd1['rnk']<rnk_ub][sd1['rnk']>rnk_lb] # range of stocks in year1
    sd2rsl = sd2[sd2['rnk']<rnk_ub][sd2['rnk']>rnk_lb] # range of stocks in year2
    adds = sd2rsl[ ~sd2rsl['cusip'].isin(sd1rsl['cusip'])]
    dels = sd1rsl[ ~sd1rsl['cusip'].isin(sd2rsl['cusip'])]

    ls_add_n.append(adds.shape[0])
    ls_del_n.append(dels.shape[0])
    
    # Calculate entering and existing date
    # date2 is the existing date    
    ed = int(yr2*1e4 + mth_e*1e2 + dt_e)
    
    # Form the portfolio
    sdata_add = formPort( sdata, adds, 1, 'mktcp')
    # sdata_add = formPort( sdata, adds, 1, 'equal')
    sdata_del = formPort( sdata, dels, -1, 'mktcp')    
    # sdata_del = formPort( sdata, dels, 1, 'equal')
    sdata_prt=sdata_add.append( sdata_del)
    # Calculate daily price of the portfolio
    p_d=sdata_prt.groupby('datadate')['prt'].sum() #.to_frame() #.tolist() 
    
    # Calculate daily return of the portfolio        
    #Failed Attempt    
    #p_d['datadate']=p_d.index
    #p_d['dt_rnk']=p_d['datadate'].rank(ascending=True)
    #p_d['dt_rnk-1']=p_d['dt_rnk']-1
    #p_d.join( p_d, on=['dt_rnk', 'dt_rnk'], how='inner')        
    rt_s=[] # list of daily return 
    rt_c=[]  # list of cumulative return 
    dt_s=[] # list of daily date

    for prti in range(1, len(p_d)):
        rti=p_d.iloc[prti]/p_d.iloc[prti-1]-1 # Cumulative simple return
        rti_c=p_d.iloc[prti]/p_d.iloc[0]-1 # intraday simple return
        if(rti<0.5 and -0.5<rti and rti_c<1 and rti_c>-1):
            rt_s.append(rti) # list of daily return during investing period
            rt_c.append(rti_c)  # list of cumulative return 
            dt_s.append(p_d.index[prti]) # list of daily return during investing period  
    
    # Store daily return of the portfolio  
    ls_prt_rt.append((list, rt_s))
    rt_s_all.extend(rt_s) # append works in a wrong way
    rt_c_all.extend(rt_c)
    
    #----------------Evaluate the Strategy-------------#
    [rts, stds, spr, var5, var10, cvar5, cvar10] = eva(rt_s)
    Avg_Return.append(rts) # list of portfolio's returns
    Std_Dev.append(stds) # list of portfolio's volatility(Standard Deviation)
    Sharp_Ratio.append(spr) # list of portfolio's Sharp ratio
    VaR_5prct.append(var5) # list of portfolio's 5% VaR
    VaR_10prct.append(var10) # list of portfolio's 10% VaR 
    CVaR_5prct.append(cvar5) # list of portfolio's 5% CVaR
    CVaR_10prct.append(cvar10) # list of portfolio's 10% CVaR          
    #-Plot the return distribution and pnl time-series 
    plotReturn(rt_s, yr2, 60, 'Interday') 
    plotReturn(rt_c, yr2, 60, 'Cumulative') 

# evaluate the strategy overall    
[rts, stds, spr, var5, var10, cvar5, cvar10] = eva(rt_s_all)
Avg_Return.append(rts) # list of portfolio's returns
Std_Dev.append(stds) # list of portfolio's volatility(Standard Deviation)
Sharp_Ratio.append(spr) # list of portfolio's Sharp ratio
VaR_5prct.append(var5) # list of portfolio's 5% VaR
VaR_10prct.append(var10) # list of portfolio's 10% VaR 
CVaR_5prct.append(cvar5) # list of portfolio's 5% CVaR
CVaR_10prct.append(cvar10) # list of portfolio's 10% CVaR
plotReturn(rt_s_all, str(yrb)+' - '+str(yre), 60, 'Interday') # plot the return distribution and pnl time-series 
plotReturn(rt_c_all, str(yrb)+' - '+str(yre), 60, 'Cumulative') # plot the return distribution and pnl time-series 

ls_yr=[str(i) for i in range(yrb+1, yre+1)]
ls_yr.append('Overall')
eva_mtx=pd.DataFrame.from_items([ \
    ('index',ls_yr),('Avg_Return',Avg_Return),
    ('Std_Dev',Std_Dev),('Sharp_Ratio',Sharp_Ratio),
    ('VaR 5%',VaR_5prct),('VaR 10%',VaR_10prct),
    ('CVaR 5%',CVaR_5prct),('CVaR 10%',CVaR_10prct)])


