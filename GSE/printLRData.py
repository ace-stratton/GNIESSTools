"""
Script to open housekeeping from rocket telemetry and plot or display housekeeping for GNIESS Rocket

Author: Ace Stratton
Date: 10/22/25

V1.0 

"""
"""
INPUTS
"""

HKFILENAME = 'S1_UCB_LR_HEX_sine_test.csv'
YEAR = 2025
##################### End Inputs ##################################
import csv 
from datetime import datetime, timedelta
import pandas as pd


def parseHousekeeping(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader) #skip headers: S2_UCB_HK_Time,S2_UCB_LR
        row_count = 0
        for row in reader:
            row_count = row_count + 1
            seconds_since_start = row[0] #seconds since beginning of year 
            seconds_since_start = float(seconds_since_start)
            start_of_year = datetime(YEAR, 1, 1, 0, 0, 0)
            timestamp = start_of_year + timedelta(seconds=seconds_since_start)
            hex_value = int(row[1]) #decimal value of serial 16 bit read out
            data = format(dec_value, '016b') #converts decimal number to binary string of 16 bytes
            [ID_Name, val, errorFlag] = pull_values(data)

            if errorFlag == 'true':
                errorflags.append({
                    'timestamp': datetime.strftime(timestamp, dateformat) ,
                    'ID_Name': ID_Name,
                    'value': val, 
                    'row_idx': row_count
                })
            data_frame["TimeStamp"].append(datetime.strftime(timestamp, dateformat))
            data_frame[ID_Name].append(val)
    return data_frame, errorflags
