# -*- coding: utf-8 -*-
"""
Created on Sun Mar 19 21:31:46 2017

@author: Zhong Zeng

Python 2.7 in Spyder
"""

import numpy as np
import pandas as pd
import scipy as sp
import statsmodels.api as sm
import matplotlib.pyplot as plt

# Set path of modified csv files (change cell format in xlsx and save as csv)
path = 'F:\Michael\Fordham_University\Alternative_Investment\Fx_monentum\\'
file_list = 'list.csv' # list of currencies
file_fsv = 'fsv.csv' # forward and spot rate data with date format
# file_fnv = 'fsn.csv' # forward and spot rate data with date as numbers
fst_r = 3 # first row of data in csv or Excel files
n_c = 4 # Number of columns for each currency

# Main Script
# Read list of currencies into Pandas Dataframe
cny_ls = pd.read_csv( path + file_list, usecols=range(0, 2)) 
no_cny = cny_ls.shape[0] / 2 # number of currencies

# Read spot and forward rates into Pandas Dataframe
s_ls = [] # list of spot rates
f_ls = [] # list of forward rates
c_ls = [] # list of valid currencies
for i in range(0, no_cny): # range(0, no_cny )
    spt_rt = pd.read_csv( path + file_fsv, header=fst_r, usecols=range(10*i+5, 10*i+9)) #, dtype =  np.float64
    fwd_rt = pd.read_csv( path + file_fsv, header=fst_r, usecols=range(10*i+10, 10*i+14)) #, dtype =  np.float64

    if spt_rt.isnull().any().any()==False and fwd_rt.isnull().any().any()==False: # View Data Type # fsv.dtypes
        s_ls.append(spt_rt)
        f_ls.append(fwd_rt)
        c_ls.append(cny_ls.iloc[i*2, 0])
    
    # No Need to Fit NaN in Dataframe, As Done in BBG

# Implement Momentum Strategy
v_cny = len(c_ls) # number of currencies w/ valid data
rt_all = [] # list of Mom(f, h) returns
sr_all = [] # list of Mom(f, h) Sharp ratios
for i in range(0, v_cny): # v_cny   
    spt_rt = s_ls[i] # Cols: Date, bid, ask, mid
    fwd_rt = f_ls[i] # CAUTION! Forward rates are quoted in basis point differences from spot rate    
    # Calculating Excess Return    
    rx = spt_rt.iloc[:-1, 3].values + fwd_rt.iloc[:-1,3].values / 10000 - spt_rt.iloc[1:,3].values
    
    '''    
    # Calculating Monthly Excess Return   
    rt_mtl = rx[::30]    
    #Calculting Returns of Momentum Strat (1, 1)   
    rt_ = rt_mtl[1:][rt_mtl[:-1]>0]
    '''
    
    rt = np.empty((5, 5))
    sr = np.empty((5, 5))
    for i in range(0,5):
        if i==0:
            f = 1
        else:
            f = i*3

        for j in range(0,5):
            if j==0:
                h = 1
            else:
                h = j*3
            # Calculating Excess Return over Previous f Month
            i_f = 0
            rx_f = rx[ f-i_f: -h-i_f]
            for i_f in range(1,f):
                rx_f = rx_f + rx[ f-i_f: -h-i_f]
            rx_f = rx_f / f
            
            # Calculating Excess Return for Holding h Month
            i_h = 0
            rx_h = rx[ f+i_h: -h+i_h]
            for i_f in range(1,h):
                rx_h = rx_h + rx[ f+i_h: -h+i_h]
            rx_h = rx_h / h
            
            # Formating Portfolio
            rx_m = rx_h[rx_f>0]
            # Calculating the Return of Mom(h,l)
            rt[i][j] = sum(rx_m) /rx_h.shape # total return divided by the total number of months
            # Calculating the Sharp Ratio of Mom(h,l)
            sr[i][j] = rt[i][j] / np.std(rx_m)
            
    rt_all.append(rt)
    sr_all.append(sr)

       