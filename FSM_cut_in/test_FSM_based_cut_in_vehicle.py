"""Adversarial Vehicle Control Framework Utilizing Finite State Machine"""

import os
import csv
from datetime import datetime
from FSM_based_cut_in_environment import OneCarHighwayEnv
from data_recorder import DataRecorder
import numpy as np

# 1. Create data recording setup
# Configure log path
TEST_BASE_DIR = ".\output\cutin_fsm_testing_logs"
os.makedirs(TEST_BASE_DIR, exist_ok=True)

# Create subdirectory by time
current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
DATE_DIR = os.path.join(TEST_BASE_DIR, current_time)
CSV_SUBDIR = f"testing_log_{current_time}"
TEST_DIR = os.path.join(DATE_DIR, CSV_SUBDIR)
os.makedirs(TEST_DIR, exist_ok=True)

# Generate timestamped filename
TEST_CSV_FILENAME = f"step_log_{current_time}.csv"

# CSV file path
TEST_LOG_PATH = os.path.join(TEST_DIR, TEST_CSV_FILENAME)
# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------Data writer creation------------------------------------------------
# 1. Create table header
test_log_file = open(TEST_LOG_PATH, mode='w', newline='', encoding='utf-8')
test_csv_writer = csv.writer(test_log_file)

# 2. Create recorder and write header
recorder = DataRecorder(test_csv_writer)
recorder.init_testing_log()

# 3. Create testing environment
scenario_csv_path = './output/merged_all_scenarios.csv'          # Merged all scenarios
test_env = OneCarHighwayEnv(render_mode="rgb_array", scenario_csv_path=scenario_csv_path)

test_env.use_smart_controller = True

for i in range(748):
    obs, info = test_env.reset()
    done = False
    step_count = 0
    episode_reward = 0

    while not done and step_count < 400:
        obs, reward, done, truncated, info = test_env.step(0)
        step_count += 1

        test_env.render()

        bv = test_env.controlled_vehicles[0]
        av = test_env.road.vehicles[1]
        ttc_lon = test_env.calculate_ttc_lon(bv, av)
        distance = test_env.get_distance(bv, av)
        acceleration = bv.action["acceleration"]
        steering = bv.action["steering"]

        recorder.record_testing_data(i, step_count, f"{bv.position[0]:.6f}", f"{bv.position[1]:.6f}",
                                    f"{bv.speed:.6f}", f"{np.degrees(bv.heading):.6f}",
                                    f"{acceleration:.6f}", f"{np.degrees(steering):.6f}",
                                     f"{av.position[0]:.6f}", f"{av.position[1]:.6f}", f"{av.speed:.6f}",
                                     ttc_lon, bv.crashed, f"{distance:.6f}"
                                     )

        if done or truncated:
            break

    test_env.close()

