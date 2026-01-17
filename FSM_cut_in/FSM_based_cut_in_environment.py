"""
Construction of an Adversarial Cut-in Environment Based on Finite State Machine

Configuring FSM-based adversarial cut-in vehicles in the highway-env simulation to generate
aggressive driving behaviors against IDM vehicles within the environment.
"""

from highway_env import utils
from highway_env.envs.highway_env import HighwayEnv
from highway_env.vehicle.controller import MDPVehicle
from highway_env.utils import near_split
from highway_env.road.road import Road, RoadNetwork
import numpy as np
import pandas as pd
# Created rule-based lane change model - Finite State Machine
from FSM_based_cut_in_vehicle import SmartCutInController

class OneCarHighwayEnv(HighwayEnv):
    def __init__(self, config=None, render_mode=None, scenario_csv_path=None):
        # Initial State Collection for Cut-in Scenarios: Extracted from highD dataset,
        # with extraction process available at https://github.com/CXY118/highD-scenario-extractor.git
        self.scenario_csv_path = scenario_csv_path

        self._load_scenarios_from_csv()

        # Added: Controller instance
        self.cut_in_controller = None

        super().__init__(config, render_mode)

    @classmethod
    def default_config(cls) -> dict:
        config = super().default_config()
        config.update({
            "observation": {
                "type": "HKinematics",
                "vehicles_count": 2,
                "see_behind": True,
            },
            "action": {
                "type": "DiscreteMetaAction",
                "target_speeds": np.arange(17, 37, 1),
                "longitudinal": True,
                "lateral": True,
                "steering_range": [-np.pi / 90, np.pi / 90],
                "acceleration_range": [-4, 4],
            },
            "simulation_frequency": 40,
            "policy_frequency": 5,
            "scaling": 4.0,
            "lanes_count": 3,
            "vehicles_count": 1,
            "controlled_vehicles": 1,
            "initial_lane_id": None,
            "duration": 20,
            "ego_spacing": 2,
            "vehicles_density": 1,
            "normalize_reward": True,
            "offroad_terminal": True,
        })
        return config

    def _create_road(self) -> None:
        """Create a road composed of straight adjacent lanes."""
        self.road = Road(
            network=RoadNetwork.straight_road_network(
                self.config["lanes_count"], speed_limit=35,
                nodes_str=("A", "B")
            ),
            np_random=self.np_random,
            record_history=self.config["show_trajectories"],
        )

    def _create_vehicles(self) -> None:
        """Create some new random vehicles of a given type, and add them on the road."""

        # Get next uniform sampling point
        sample = self._get_next_uniform_sample()
        distance, bv_speed, av_speed, lane_offset = sample.values()
        bv_lane = 1 + int(lane_offset)

        other_vehicles_type = utils.class_from_path(self.config["other_vehicles_type"])
        other_per_controlled = near_split(
            self.config["vehicles_count"], num_bins=self.config["controlled_vehicles"]
        )

        self.controlled_vehicles = []

        for others in other_per_controlled:
            bv_vehicle = MDPVehicle.create_random(
                self.road,
                lane_from="A",
                lane_to="B",
                speed=bv_speed,
                lane_id=bv_lane,
                spacing=self.config["bv_spacing"],
            )
            bv_vehicle = self.action_type.vehicle_class(
                self.road, bv_vehicle.position, bv_vehicle.heading, bv_vehicle.speed
            )
            self.controlled_vehicles.append(bv_vehicle)
            self.road.vehicles.append(bv_vehicle)

            for _ in range(others):
                av_vehicle = other_vehicles_type.create_random(
                    self.road,
                    lane_from="A",
                    lane_to="B",
                    speed=av_speed,
                    lane_id=1,
                    spacing=1 / self.config["vehicles_density"],
                )
                av_vehicle.randomize_behavior()
                self.road.vehicles.append(av_vehicle)

        # Initialize smart controller
        self.cut_in_controller = SmartCutInController()

        # Record sampling information
        self.current_sample = {
            'distance': distance,
            'bv_speed': bv_speed,
            'av_speed': av_speed,
            'lane_offset': lane_offset,
        }
        print(self.current_sample)

    def _get_next_uniform_sample(self):
        """Get next uniform sampling point"""
        if self._sample_index >= len(self._all_scenarios):
            self._sample_index = 0
            print("Starting new uniform sampling cycle")

        sample = self._all_scenarios[self._sample_index]
        self._sample_index += 1
        return sample

    def _load_scenarios_from_csv(self):
        """Load scenario data from CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(self.scenario_csv_path)
            # Check required columns
            required_columns = ['x_diff_abs', 'xVelocity_cut_in', 'xVelocity_target', 'adjusted_laneId_diff']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Missing required column in CSV file: {col}")

            # Convert to scenario list
            _all_scenarios = []
            for _, row in df.iterrows():
                scenario = {
                    'distance': float(row['x_diff_abs']),
                    'bv_speed': abs(float(row['xVelocity_cut_in'])),
                    'av_speed': abs(float(row['xVelocity_target'])),
                    'lane_offset': int(row['adjusted_laneId_diff'])
                    }
                _all_scenarios.append(scenario)

            print(f"Successfully loaded {len(_all_scenarios)} scenarios")

        except Exception as e:
            print(f"Failed to load CSV file: {e}")
            raise

        self._sample_index = 0

    def _reset(self) -> None:
        super()._reset()
        self.road.record_history = True

        # Override longitudinal position
        self.road.vehicles[1].position[0] = self.controlled_vehicles[0].position[0] + self.current_sample['distance']

        # Reset controller
        if hasattr(self, 'cut_in_controller') and self.cut_in_controller is not None:
            self.cut_in_controller.reset()

    def step(self, action):
        # Get vehicle objects
        bv = self.controlled_vehicles[0]
        av = self.road.vehicles[1]

        # Determine whether to use controller
        use_controller = False

        # Condition 1: If controller exists
        if hasattr(self, 'cut_in_controller') and self.cut_in_controller is not None:
            # Condition 2: Can set a flag to decide whether to use controller
            if hasattr(self, 'use_smart_controller') and self.use_smart_controller:
                use_controller = True

        if use_controller:
            # Use smart controller for decision
            controller_action = self.cut_in_controller.get_action(bv, av)

            if self.steps % 1 == 0:
                action_names = ["LANE_LEFT", "IDLE", "LANE_RIGHT", "FASTER", "SLOWER"]
                print(f"Step {self.steps} Controller state: {self.cut_in_controller.phase}, "
                      f"Action: {action_names[controller_action]}")

            action = controller_action

        result = super().step(action)

        return result

    def calculate_ttc_lon(self, bv, av):
        bv_length = 5
        av_length = 5
        bv_x = bv.position[0]
        av_x = av.position[0]

        bv_speed = abs(bv.speed * np.cos(bv.heading))
        av_speed = abs(av.speed * np.cos(av.heading))

        if bv.lane_index[-1] == av.lane_index[-1]:
            if bv_x > av_x:
                rel_x = (bv_x - bv_length / 2) - (av_x + av_length / 2)
            else:
                rel_x = (av_x - av_length / 2) - (bv_x + bv_length / 2)
        else:
            rel_x = abs(bv_x - av_x)

        closing_speed = bv_speed - av_speed

        if bv_x > av_x:
            if closing_speed > 0:
                return float('inf')
            else:
                return rel_x / abs(closing_speed)
        else:
            if closing_speed < 0:
                return float('inf')
            else:
                return rel_x / closing_speed

    def get_distance(self, bv, av):

        bv_x = bv.position[0]
        av_x = av.position[0]
        bv_y = bv.position[1]
        av_y = av.position[1]
        distance = ((bv_x - av_x) ** 2 + (bv_y - av_y) ** 2) ** 0.5

        return distance

    def _is_terminated(self) -> bool:
        return super()._is_terminated()

    def _is_truncated(self) -> bool:
        return super()._is_truncated()