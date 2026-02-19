"""
Script to open Saleae data from the DEB and plot the results. Inputs must be in Binary!!!
Files must be named 'BIN_<Voltage>_<CH>_

Author: Ace Stratton
Date: 10/15/25

V1.0 - 11/13/25

"""


"""
INPUTS -- CHANGE THESE AS NEEDED
"""
##################### Begin Inputs ##################################
HKFILENAME = 'WFFInputFiles\S1_UCB_LR_HEX_36398_Flight_8M_Antenna_.csv'
SELECTED_CH = 'All'
NUM_SAMPLES = 7000000#6091897 #97
saveMag = False
t0 = 3579570 #3579540 #397
##################### End Inputs ##################################

import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MaxNLocator

def twos_from_bin_16(b):
    val = int(b, 2)
    if b[0] == '1':        # MSB = sign bit
        val -= 1 << 16
    return val


ch_idx  = {
    "bx": 0,
    "by": 1,
    "bz": 2,
    "vdc1": 3,
    "vdc2": 4,
    "vdc3": 5,
    "vdc4": 6,
    "edc12": 7,
    "edc34": 8,
}

if HKFILENAME[0] == 'S':
    title = f"{HKFILENAME[20:-4]}_{SELECTED_CH}"
elif HKFILENAME[0] == 'W':
    title = f"{HKFILENAME[14:-4]}_{SELECTED_CH}"
             #removing .csv

with open(HKFILENAME, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        next(reader) #skip headers: S2_UCB_HK_Time,S2_UCB_HK
        output_data=[]
        idx = 0
        count = 0
        for row in reader:
            if SELECTED_CH == 'All':
                if idx == 9:
                    idx = 0
                    continue
                timestamp = round(float(row[0]), 5) - t0
                if HKFILENAME[0] == 'S':    
                    data_ch = int(row[3], 16)
                elif HKFILENAME[0] == 'W':
                    data_ch = int(row[1], 16)
                output_data.append([timestamp, data_ch])
                idx = idx + 1
                count = count + 1

                if count == NUM_SAMPLES:
                    break

            else:
                if idx == ch_idx[SELECTED_CH]:
                    timestamp = round(float(row[0]), 5)
                    # data_str = row[3]
                    # data_str_cleaned = (data_str[4:]).replace(" ", "")
                    # data_ch = twos_from_bin_16(data_str_cleaned)
                    if HKFILENAME[0] == 'S':    
                        data_ch = int(row[3], 16)
                    elif HKFILENAME[0] == 'W':
                        data_ch = int(row[1], 16)
                    output_data.append([timestamp, data_ch])
                    count = count + 1
                
                if count == NUM_SAMPLES:
                      break
                if idx == 9:
                      idx = 0
                else:
                      idx = idx + 1
                


                # bx = twos_from_bin_16(bx)
                # by = twos_from_bin_16(by)
                # bz = twos_from_bin_16(bz)
                # vdc1 = twos_from_bin_16(vdc1)
                # vdc2 = twos_from_bin_16(vdc2)
                # vdc3 = twos_from_bin_16(vdc3)
                # vdc4 = twos_from_bin_16(vdc4)
                # edc12 = twos_from_bin_16(edc12)
                # edc34 = twos_from_bin_16(edc34)

        if SELECTED_CH == 'All':
            fig, axs = plt.subplots(3, 3, figsize=(10, 10))
            arr = np.array(output_data)
            length = len(arr) - round((len(arr)/9 - round(len(arr)/9))*9)
            times = arr[0:length,0].reshape(-1, 9).T 
            vals = arr[0:length,1].reshape(-1, 9).T  # transpose to group by column
            idx = 0
            for i in range(3):
                for j in range(3):
                    key = next(k for k, v in ch_idx.items() if v == (idx))
                    axs[i,j].plot(times[idx], vals[idx])
                    axs[i,j].set_title(f"{key}")
                    idx = idx + 1
                    ax = plt.gca()
                    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))  # ~6 ticks
                    axs[i,j].grid(True)
            fig.suptitle(title)
            fig.supxlabel("Time[s]")
            fig.supylabel("Counts")
            fig.tight_layout()
            manager = plt.get_current_fig_manager()
            #manager.full_screen_toggle()  # enter fullscreen
            plt.savefig(f"GeneratedPlots/{title}.png", dpi=300)

            if saveMag:
                with open(f'GeneratedFiles/{title}.csv', 'w', newline="") as f:
                    fieldnames = ['time_bx', 'bx', 'time_by', 'by', 'time_bz', 'bz']
                    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
                    writer.writeheader()
                    indx = 0
                    for indx in range(NUM_SAMPLES):
                        row = {
                                'time_bx': times[0,indx], 
                                'bx': vals[0,indx], 
                                'time_by': times[1,indx], 
                                'by': vals[1,indx], 
                                'time_bz': times[2, indx], 
                                'bz': vals[2,indx]
                            }
                        writer.writerow(row)



            
        else:       
            data = pd.DataFrame(output_data, columns=['Time', SELECTED_CH])
            plt.plot(data['Time'], data[SELECTED_CH])               
            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(nbins=6))  # ~6 ticks
            plt.xlabel("Time[s]")
            plt.ylabel("Counts")
            plt.title(title)
            plt.grid(True)
            plt.tight_layout
            plt.savefig(f"GeneratedPlots/{title}.png", dpi=300)
        

        

        

        plt.show()



