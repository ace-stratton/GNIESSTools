"""
Script to open housekeeping from rocket telemetry and plot or display housekeeping for GNIESS Rocket. 


Author: Ace Stratton
Date: 10/15/25

V2.0 - 10/23/25

"""


"""
INPUTS -- CHANGE THESE AS NEEDED
"""
##################### Begin Inputs ##################################
HKFILENAME = 'S2_UCB_HK_HEX_sine_test.csv'
YEAR = 2025
OUTPUT_FILE_ID = 'FPGASineWaveTest'
FPGA_Version = 2
##################### End Inputs ##################################

# DO NOT EDIT ANYTHING PAST THIS POINT


import csv 
from datetime import datetime, timedelta
import pandas as pd

dateformat = "%Y-%m-%d_%H-%M-%S-%f"


"""
Creates Dictionary of HK values and their ID's from 6 MSBs
"""
hk = {
    "000000": "FPGA_v",
    "000010": "Counter",
    "000100": "P5V_VMON",
    "000101": "N5V_VMON",
    "000110": "P15V_VMON",
    "000111": "N15V_VMON",
    "001000": "P24V_VMON",
    "001001": "P15V_IMON",
    "001010": "N15V_IMON",
    "001011": "P24V_IMON",
    "001100": "P28V_IMON",
    "001101": "P28V_VMON",
    "001110": "P5V_IMON",
    "001111": "N5V_IMON",
    "010000": "3v3_IMON",
    "010001": "1v5_IMON",
    "010010": "3v3_VMON",
    "010011":"2v5_VMON",
    "010100": "1v5_VMON"
}
expected_vals = {
    "FPGA_v": 2,
    "Counter": 0,
    "P5V_VMON": 1.967,
    "N5V_VMON": 1.623,
    "P15V_VMON": 1.949,
    "N15V_VMON": 1.991,
    "P24V_VMON": 2.185,
    "P15V_IMON": 0.282,
    "N15V_IMON": 2.127,
    "P24V_IMON": 0.119,
    "P28V_IMON": 0.884,
    "P28V_VMON": 1.797,
    "P5V_IMON": 0.707,
    "N5V_IMON": 3.263,
    "3v3_IMON": 0.417,
    "1v5_IMON": 0.587,
    "3v3_VMON": 3.3,
    "2v5_VMON": 2.5,
    "1v5_VMON": 1.559
}

data_frame = {
    "TimeStamp": [],
    "FPGA_v": [],
    "Counter": [],
    "P5V_VMON": [],
    "N5V_VMON": [],
    "P15V_VMON": [],
    "N15V_VMON": [],
    "P24V_VMON": [],
    "P15V_IMON": [],
    "N15V_IMON": [],
    "P24V_IMON": [],
    "P28V_IMON": [],
    "P28V_VMON": [],
    "P5V_IMON": [],
    "N5V_IMON": [],
    "3v3_IMON": [],
    "1v5_IMON": [],
    "3v3_VMON": [],
    "2v5_VMON": [],
    "1v5_VMON": []
}

wd_size = 16 # word size is 16 bits

def pull_values(binary):
    """
    Pulls ID and data value of the serial input, it then converts the ID to the corresponding name and
    it converts the value to real numbers and returns
    """
    ID = binary[0:6]  
    ID_name = hk[ID]
    expected_val = float(expected_vals[ID_name])
    val_binary = binary[6:] #Grabbing values from rest of binary string
    val_ADC = int(val_binary,2)

    if int(ID,2) > 2:
        val_binary = binary[6:] #Grabbing values from rest of binary string
        val_ADC = int(val_binary+'00',2)
        value = (((val_ADC)/4095)*5.15) #converting from bit count of ADC to decimal value 
    else:
        val_binary = binary[6:] #Grabbing values from rest of binary string
        val_ADC = int(val_binary,2) 
        value = val_ADC
        
    if expected_val != 0 and int(ID,2) > 2:
        error = abs(value-expected_val)/expected_val 
        if error > 0.05 and 'VMON' in ID_name: #acceptable error for VMON values is 5%
            errorFlag = 'true'
        elif error > 0.2 and 'IMON' in ID_name and '15' not in ID_name:
            errorFlag = 'true'
        elif error > 0.25 and '15V_IMON' in ID_name:
            errorFlag = 'true'
        else:
            errorFlag = 'false'
    elif int(ID,2) == 0:
        if val_ADC != FPGA_Version:
            errorFlag = 'true'
        else:
            errorFlag = 'false'
    elif int(ID,2) == 2:
        errorFlag = 'NA'


    return(ID_name, value, errorFlag)



def parseHousekeeping(filename):
    with open(filename, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader) #skip headers: S2_UCB_HK_Time,S2_UCB_HK
        errorflags = []
        row_count = 0
        counter = 0
        for row in reader:
            row_count = row_count + 1
            seconds_since_start = row[0] #seconds since beginning of year 
            seconds_since_start = float(seconds_since_start)
            start_of_year = datetime(YEAR, 1, 1, 0, 0, 0)
            timestamp = start_of_year + timedelta(seconds=seconds_since_start)
            dec_value = int(row[1], 16) #decimal value of serial 16 bit read out
            data = format(dec_value, '016b') #converts decimal number to binary string of 16 bytes
            try:
                [ID_Name, val, errorFlag] = pull_values(data)
            except Exception:
                continue
            
            if errorFlag == 'NA':
                if val > counter:
                    errorFlag = 'false'
                else:
                    errorFlag = 'true'
                counter = val

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


data, errorflags = parseHousekeeping(HKFILENAME)

if errorflags:
    with open('ErrorReport.csv', 'w', newline="") as f:
        fieldnames = ['timestamp', 'ID_Name', 'value', 'row_idx']
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
        writer.writeheader()
        for err in errorflags:
            row = {
                    'timestamp': err['timestamp'],
                    'ID_Name': err['ID_Name'],
                    'value': err['value'], 
                    'row_idx': err['row_idx']
                }
            writer.writerow(row)
    print(f"There was an error: Error log saved to csv")
else:
    print("No errors found, yay! :)")

df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in data_frame.items()]))
df.to_csv(f"Output/HKData_{data["TimeStamp"][0]}_{OUTPUT_FILE_ID}.csv", index=False)
print(f"Saved data to file Output/HKData_{data["TimeStamp"][0]}_{OUTPUT_FILE_ID}.csv")
