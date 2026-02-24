import matplotlib.pyplot as plt
import pandas as pd

"""
Script to plot a Period vs Flow Rate error bar graph
"""

# Load csv
df = pd.read_csv("dataframe-2Full.csv")
#plt.style.use('dark_background')

# Remove small flowrates
flow_rates = df['Flow rate'].unique()
min_flow_rate = 2
df = df[df['Flow rate'] > min_flow_rate]

plt.figure(figsize=(18.5, 10.5))

# Plot Period vs Flow Rate graph
markers, caps, bars = plt.errorbar(df['Flow rate'], df['Period'], yerr=df['STD Period'], fmt='.',
                                   ecolor='red')

markers.set_markersize(1)

# Change alpha on error bars
[bar.set_alpha(0.1) for bar in bars]
[cap.set_alpha(0.1) for cap in caps]

plt.xlabel("Flow Rate (drops/s)")
plt.ylabel("Period (s)")

plt.tight_layout()
plt.show()