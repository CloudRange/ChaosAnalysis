from sklearn.neighbors import NearestNeighbors
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation
from sklearn.cluster import DBSCAN

"""
Script to save and display an animation with a figure with two plots: Period vs n and Period vs Period + 1, for 
different flow rates. DBSCAN is used on the Period vs Period + 1 to show clusters of data.
"""

def k_neighbours(x):
    """
    Function to calculate the optimal epsilon for use on DBSCAN using the elbow method.
    Uses K-neighbors to find the distances between points, and the calculates a perpendicular line to where the elbow
    should be the optimal value from a triangle created from the points:
    (x[0][0], x[1][0]), (x[0][-1], x[1][0]), (x[0][-1], x[0][-1]).

    args:
        x: 2D array
    return:
        distances[result_index]*3: used for epsilon for DBSCAN. Largest perpendicular vector from the
        hypotenuse of a right angle created from points (x[0][0], x[1][0]), (x[0][-1], x[1][0]), (x[0][-1], x[0][-1])
    """


    kneigh = NearestNeighbors(n_neighbors=20).fit(x)
    distances, indices = kneigh.kneighbors(x)

    distances = np.sort(distances, axis=0)[:, 1]



    # Covert into a matrix of coordinates, first column n, second value of distance.
    position_matrix = np.vstack((range(len(distances)), distances)).T

    # Subtract the initial point from the rest to get their vectors compared to the first point
    vector_from_first = position_matrix - position_matrix[0]

    # Hypotenuse of a right angle triangle with points:
    # (0,distances[0]), (len(distances) ,distances[-1]), (len(distances), distances[0])
    # should always be position_matrix[-1] as long as position_matrix[0] is 0,0.
    line_vector = position_matrix[-1] - position_matrix[0]

    # Get normal Vector of the line_vector
    line_vector_norm = line_vector / np.sqrt(np.sum(line_vector ** 2))




    # Create a matrix of the normal Vector of the line_vector with the same size as vector_from_first and do a
    # matrix multiplication
    mult_vector = vector_from_first * np.tile(line_vector_norm, (len(distances), 1))

    # Calculate the dot product of all points (sum the x and y axis for each point), result is a list of results
    dot_product = np.sum(mult_vector, axis=1)

    # Calculate the outer product of the scalar product and the line vector normal
    distance_vector = np.outer(dot_product, line_vector_norm)

    # Calculate the vector connecting the line_vector and the vector from the point to the first point,
    # and their magnitude. The vector_to_line should be perpendicular to the line_vector
    vector_to_line = vector_from_first - distance_vector
    distance_to_line = np.sqrt(np.sum(vector_to_line ** 2, axis=1))

    # The largest magnitude is considered the "elbow" of the curve and used as the epsilon for the DBSCAN.
    # return it multiplied by 3 to overcompensate the epsilon
    result_index = np.argmax(distance_to_line)


    """
    Deprecated
    Code to plot the result of the optimal elbow point 
    
    plt.plot(distances)
    plt.plot([0, result_index],[distances[-1], distances[result_index]])
    plt.plot([0, len(distances) -1],[0, distances[-1]])
    plt.scatter(result_index, distances[result_index])
    plt.show()
    """
    if distances[result_index] <= 0:
        distances[result_index] = .00005

    return distances[result_index]*3

def initialize_plot(i):
    """
    Function used to plot a figure with 2 plots: Period vs n and Period vs Period + 1 (The following period from that
    data point), using DBSCAN to showcase clusters of data in the Period vs Period + 1 graph, for a flow rate (i).

    args:
        i:  Flow Rate (String)
    """


    curr_df = df[df['Flow rate'] == flow_rates[i]]
    curr_df.reset_index(drop=True, inplace=True)


    # Plot Period vs N graph
    number = range(1, len(curr_df['Period']) + 1)
    curr_plot_1 = axis[0].errorbar(number, curr_df['Period'], yerr=curr_df['STD Period'], fmt='.',
                                               ecolor='red')

    # Change alpha on error bars
    [bar.set_alpha(0.1) for bar in curr_plot_1[2]]
    [cap.set_alpha(0.1) for cap in curr_plot_1[1]]

    # Use DBSCAN function to find the number of clusters and their corresponding points
    X = curr_df[['Period', 'Period + 1']].to_numpy()
    epsilon = k_neighbours(X)
    db = DBSCAN(eps=epsilon, min_samples=10).fit(X)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    unique_labels = set(labels)


    # Plot each label group in a different color
    colors = ['lightpink', 'blueviolet', 'royalblue', 'lime', 'coral', 'darkred', 'gold', 'cyan', 'magenta',
              'aquamarine']
    for k, col in zip(unique_labels, colors):
        # If not in a group point is black
        if k == -1:
            col = 'black'

        # Plot only the current label group
        class_member_mask = (labels == k)
        xy = X[class_member_mask]

        curr_plot_2 = plt.errorbar(xy[:, 1], xy[:, 0], fmt='o', markerfacecolor=col, markeredgecolor='k', markersize=6,
                                   yerr=curr_df['STD Period'][0], xerr=curr_df['STD Period'][0], ecolor=col)

        # Change alpha on error bars
        [bar.set_alpha(0.1) for bar in curr_plot_2[2]]
        [cap.set_alpha(0.1) for cap in curr_plot_2[1]]



    # Set axis and subtitles for the whole figure

    figure.suptitle("Flow rate = {:.4f}".format(flow_rates[i]))

    axis[0].set_xlim([0, 100])
    axis[0].set_ylim(min(curr_df['Period']) - max(curr_df['STD Period']), max(curr_df['Period'] + max(curr_df['STD Period'])))

    axis[1].set_xlim(min(curr_df['Period + 1']) - max(curr_df['STD Period']), max(curr_df['Period + 1']) + max(curr_df['STD Period']))
    axis[1].set_ylim(min(curr_df['Period']) - max(curr_df['STD Period']), max(curr_df['Period'] + max(curr_df['STD Period'])))

    axis[1].set_ylabel("Period (s)", loc='top')
    axis[0].set_xlabel("n")
    axis[1].set_xlabel("Period + 1 (s)")


    axis[0].title.set_text("Period vs n")
    axis[1].title.set_text("Period vs Period + 1\n Number of clusters:{}".format(n_clusters_))



def animate(i):
    """
        Function to clear the current plots and call the initialize_plot function.
        Separated since the initialize_plot can be used to create an individual plot
    args:
        i:  Flow Rate (String)
    """

    axis[0].clear()
    axis[1].clear()

    initialize_plot(i)


# MAIN SCRIPT

df = pd.read_csv("dataframe-2Full.csv")


min_flow_rate = 2
max_flow_rate = 10000

df = df[df['Flow rate'] >= min_flow_rate]
df = df[df['Flow rate'] <= max_flow_rate]

flow_rates = sorted(df['Flow rate'].unique())




figure, axis= plt.subplots(ncols=2,sharey=True,figsize=(20, 10),gridspec_kw=dict( wspace=.1))






initialize_plot(0)

ani = animation.FuncAnimation(figure, animate, repeat=True, frames=len(flow_rates)-1, interval=1000)


""" Uncomment this to save animation as a MP4


Writer = animation.writers['ffmpeg']
writer = Writer(fps=10, metadata=dict(artist='Etienne Cote'), bitrate=2500)
print("Saving")
ani.save('AnimationDBSCAN2.mp4', writer=writer)

"""

""" Uncomment this to save animation as a GIF

writer = animation.PillowWriter(fps=60,metadata=dict(artist='Etienne Cote'), bitrate=1800)
ani.save('AnimationDBSCAN2.gif', writer=writer)
"""

#plt.show()
print("end")


