import numpy as np
import pandas as pd
import glob


"""
Script to create a .csv file containing the raw time, period between drops, next period, flow rate, and standard 
deviation of the data collected.
"""

# Max and minimum seconds between drops that will be considered for further use
max_sec_limit = 3
min_sec_limit = -1

df = pd.DataFrame(columns=['Raw time', 'Period', 'Period + 1', 'Flow rate', 'STD Period'])


# Read the sub folders for each data taking session
#folders = glob.glob("temp/*")
folders = glob.glob("Main_data_par/*")

for i in folders:
    files = glob.glob(i + "/*.csv")
    # Read each of the .csv files in the folder, they contain 1000 datapoints of the time (μs) when a drop was detected.
    # A file was created every 1000 datapoints to avoid the measuring device timing out during prolonged sessions.
    for j in files:
        dataset = []
        with open(j, 'r') as l:
            for line in l.readlines():
                line = line.replace("\n", "")
                x = line.replace(" ", "")
                dataset.append(int(x))


        dataset = np.asarray(dataset)

        # calculate the time between each drop and convert it into seconds
        periods = (dataset[1:] - dataset[:-1])*1e-6

        # An overflow is detected by a negative period and is corrected using the overflow number for 32-bit systems
        periods[periods < 0] += 4294967295*1e-6

        # add a -1 period for the first period since the file contains no information for what came before
        periods = np.insert(periods, 0, -1)

        # create a new array that displaces the periods by 1, and add a -1 to the final one since there is no more info
        period_second = np.copy(periods[1:])
        period_second = np.append(period_second, -1)


        # The data set is split in n equal parts, the flowrate is calculated for each of those parts from the mean
        split = 4
        dataset = np.array_split(dataset, split)
        periods = np.array_split(periods, split)
        period_second = np.array_split(period_second, split)




        for k in range(split):

            df_temp = pd.DataFrame(columns=['Raw time', 'Period', 'Period + 1', 'Flow rate', 'STD Period'])

            df_temp['Raw time'] = dataset[k]
            df_temp['Period'] = periods[k]
            df_temp['Period + 1'] = period_second[k]


            # Remove outlier rows that must be caused by a blockage on the eyedropper or lack of measurement of the
            # drops in between the measured drops
            df_temp = df_temp[df_temp['Period'] > min_sec_limit]
            df_temp = df_temp[df_temp['Period + 1'] > min_sec_limit]
            df_temp = df_temp[df_temp['Period + 1'] < max_sec_limit]
            df_temp = df_temp[df_temp['Period'] < max_sec_limit]


            # Flow rate calculation for the split
            df_temp['Flow rate'] = np.mean(df_temp['Period'])**-1



            df_temp['STD Period'] = 3.5082808476358533e-05
            df_temp['STD Period'] = np.std(df_temp['Period'])
            # df_temp['STD Period'] = 0.0009554375422814145
            df = pd.concat([df, df_temp], ignore_index=True)


df.to_csv("dataframe-2Full.csv", index=False)

#df.to_csv("dataframe-test2.csv", index=False)

