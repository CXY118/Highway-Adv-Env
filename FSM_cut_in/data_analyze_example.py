"""plotting example"""

import pandas as pd
from plotter import Plotting

# CSV file path
path = '.\output\cutin_fsm_testing_logs\step_log.csv'

# Read all data
df = pd.read_csv(path)

# Select trajectory data for specific episode
episode_num = 50
episode_data = df[df.iloc[:, 0] == episode_num]

# Extract BV trajectory data
bv_x, bv_y = episode_data.iloc[:, 2], episode_data.iloc[:, 3]
# Extract AV trajectory data
av_x, av_y = episode_data.iloc[:, 8], episode_data.iloc[:, 9]

plotter = Plotting()
plotter.plot_wide_trajectory_with_last_and_lane(bv_x, bv_y, av_x, av_y)

