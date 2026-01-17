"""
An adversarial vehicle controller using finite-state machine for cut-in maneuvers.

The FSM-based controller implements aggressive cut-in behavior with three sequential phases: accelerate to overtake,
maintain overtaking position, then execute lane change. It transitions states based on relative speed and distance
thresholds to force interactions.
"""

class SmartCutInController:
    def __init__(self, target_vehicle=None):
        self.target = target_vehicle

        # State variables
        self.phase = "accelerating"           # Initial state

        # State transition parameters
        self.max_speed = 36.0
        self.overtake_distance = 5.0          # How far beyond the AV to start cutting in

        # State transition condition records
        self.acceleration_complete = False
        self.lane_change_sent = False         # Whether lane change command has been sent

    def _update_state(self, bv, av):
        """
        Automatically update state based on conditions
        bv: Vehicle generating adversarial cut-in behavior
        av: Vehicle being cut into
        """
        dx = av.position[0] - bv.position[0]  # Longitudinal distance

        # State transition logic
        if self.phase == "accelerating":
            # Condition 1: Reach near maximum speed
            if bv.speed >= self.max_speed - 1.0 and not self.acceleration_complete:
                print(f"[State Transition] Acceleration complete → Overtaking phase (Speed: {bv.speed:.1f}m/s)")
                self.phase = "overtaking"
                self.acceleration_complete = True

            # Condition 2: Already exceeded sufficient distance (even if speed is insufficient)
            elif dx < -self.overtake_distance:
                print(f"[State Transition] Distance requirement met → Direct cut-in (Exceeding AV: {-dx:.1f}m, Speed: {bv.speed:.1f}m/s)")
                self.phase = "cutting_in"
                self.acceleration_complete = True

        elif self.phase == "overtaking":
            # Transition condition: Exceed the AV by specified distance
            if dx < -self.overtake_distance:
                print(f"[State Transition] Overtaking completed → Start cut-in (Exceeding AV: {-dx:.1f}m)")
                self.phase = "cutting_in"

        elif self.phase == "cutting_in":
            # Transition condition: Complete lane change
            if self._is_same_lane(bv, av):
                print(f"[State Transition] Cut-in completed → Maintaining phase (Lane: {bv.lane_index[-1]:.1f})")
                self.phase = "maintaining"

    def _is_same_lane(self, bv, av):
        """Check if vehicles are in the same lane"""
        return abs(bv.lane_index[-1] - av.lane_index[-1]) < 0.01

    def get_action(self, bv, av):
        """Get action: First update state, then return action"""
        # 1. Update state (based on latest vehicle states)
        self._update_state(bv, av)

        # 2. Return action based on current state
        if self.phase == "accelerating":
            return self._accelerate_action(bv, av)

        elif self.phase == "overtaking":
            return self._overtake_action(bv, av)

        elif self.phase == "cutting_in":
            return self._cut_in_action(bv, av)

        elif self.phase == "maintaining":
            return self._maintain_action(bv, av)

        else:
            return 1  # IDLE

    # Action functions for each state
    def _accelerate_action(self, bv, av):
        """Acceleration phase: Accelerate fully, but check distance"""
        dx = av.position[0] - bv.position[0]

        # If already exceeded sufficient distance, immediately stop accelerating and prepare for cut-in
        if dx < -self.overtake_distance:
            print(f"[Acceleration Phase] Distance requirement met ({-dx:.1f}m), stop accelerating and wait for cut-in")
            return 1  # IDLE

        # Otherwise continue accelerating
        if bv.speed < self.max_speed:
            return 3  # FASTER
        else:
            return 1  # IDLE

    def _overtake_action(self, bv, av):
        """Overtaking phase: Maintain high speed"""
        dx = av.position[0] - bv.position[0]

        # If already exceeded sufficient distance, immediately stop accelerating
        if dx < -self.overtake_distance:
            return 1  # IDLE

        # Otherwise maintain high speed
        if bv.speed < self.max_speed - 0.5:
            return 3  # FASTER
        else:
            return 1  # IDLE

    def _cut_in_action(self, bv, av):
        """Cut-in phase: Execute lane change"""
        # Check if already in target lane
        if self._is_same_lane(bv, av):
            self.lane_change_sent = False
            return 1

        # If lane change command hasn't been sent yet, send it once
        if not self.lane_change_sent:
            self.lane_change_sent = True
            direction = self._get_lane_change_direction(bv, av)
            print(f"[Cut-in] Send lane change command: {'Left' if direction == 0 else 'Right' if direction == 2 else 'None'}")
            return direction

        return 1  # IDLE

    def _maintain_action(self, bv, av):
        """Maintaining phase: Maintain safe distance"""
        dx = av.position[0] - bv.position[0]

        # Target: Maintain 5-15 meters ahead of AV
        if dx < -20:     # BV is too far ahead
            return 4     # SLOWER
        elif dx > -10:   # BV is too far behind
            return 3     # FASTER
        else:
            return 1     # IDLE

    def _get_lane_change_direction(self, bv, av):
        """Determine lane change direction"""
        if bv.lane_index[-1] > av.lane_index[-1]:
            return 0  # LANE_LEFT
        elif bv.lane_index[-1] < av.lane_index[-1]:
            return 2  # LANE_RIGHT
        else:
            return 1  # IDLE

    def reset(self):
        """Reset all states"""
        self.phase = "accelerating"
        self.acceleration_complete = False
        self.lane_change_sent = False
        print("[Simplified Controller] States reset")