"""A visualization tool that renders vehicle trajectories"""

import matplotlib.pyplot as plt
import numpy as np

class Plotting:
    def sample_points(self, x_array, y_array, num_points=20):
        """
        Uniformly sample specified number of points from trajectory points

        Parameters:
        x_array, y_array: Original trajectory coordinates
        num_points: Number of points to sample

        Returns:
        sampled_x, sampled_y: Sampled coordinates
        """
        total_points = len(x_array)

        if total_points <= num_points:
            return x_array, y_array

        # Uniform sampling indices
        indices = np.linspace(0, total_points - 1, num_points, dtype=int)

        # Ensure inclusion of start and end points
        indices[0] = 0
        indices[-1] = total_points - 1

        return x_array.iloc[indices], y_array.iloc[indices]

    def plot_wide_trajectory_with_last_and_lane(self, bv_x, bv_y, av_x, av_y, bar_width=2.0, last_box_length=5):
        fig, ax = plt.subplots(figsize=(10, 4))

        # Get initial Y values
        bv_y_init = bv_y.iloc[0] if len(bv_y) > 0 else 0
        av_y_init = av_y.iloc[0] if len(av_y) > 0 else 0

        # Determine scenario: bv near 0 and av near 4, or bv near 4 and av near 0
        if ((abs(bv_y_init - 0) < 1 and abs(av_y_init - 4) < 1) or
                (abs(bv_y_init - 4) < 1 and abs(av_y_init - 0) < 1)):
            # Scenario 1: bv near 0, av near 4 (or vice versa)
            solid_lines = [-2, 6]  # Solid line positions
            dashed_line = 2        # Dashed line position
        elif ((abs(bv_y_init - 4) < 1 and abs(av_y_init - 8) < 1) or
              (abs(bv_y_init - 8) < 1 and abs(av_y_init - 4) < 1)):
            # Scenario 2: bv near 4, av near 8 (or vice versa)
            solid_lines = [2, 10]  # Solid line positions
            dashed_line = 6        # Dashed line position
        else:
            solid_lines = []
            dashed_line = None

        # Draw solid lines
        for y in solid_lines:
            ax.axhline(y=y, color='black', linewidth=1, linestyle='-', alpha=0.7)

        # Draw dashed line
        if dashed_line is not None:
            ax.axhline(y=dashed_line, color='black', linewidth=1, linestyle='--', alpha=0.7)

        # Draw BV vehicle
        for i in range(len(bv_x) - 1):
            x1, y1 = bv_x.iloc[i], bv_y.iloc[i]
            x2, y2 = bv_x.iloc[i + 1], bv_y.iloc[i + 1]

            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx ** 2 + dy ** 2)

            if length > 0:
                angle = np.arctan2(dy, dx)
                rect = plt.Rectangle(((x1 + x2) / 2 - length / 2, (y1 + y2) / 2 - bar_width / 2),
                                     length, bar_width,
                                     angle=np.degrees(angle),
                                     facecolor='pink', edgecolor='black',
                                     linewidth=0.5, alpha=0.7)
                ax.add_patch(rect)

        # Draw AV vehicle
        for i in range(len(av_x) - 1):
            x1, y1 = av_x.iloc[i], av_y.iloc[i]
            x2, y2 = av_x.iloc[i + 1], av_y.iloc[i + 1]

            dx, dy = x2 - x1, y2 - y1
            length = np.sqrt(dx ** 2 + dy ** 2)

            if length > 0:
                angle = np.arctan2(dy, dx)
                rect = plt.Rectangle(((x1 + x2) / 2 - length / 2, (y1 + y2) / 2 - bar_width / 2),
                                     length, bar_width,
                                     angle=np.degrees(angle),
                                     facecolor='lightblue', edgecolor='black',
                                     linewidth=0.5, alpha=0.7)
                ax.add_patch(rect)

        # Add thin black border to BV's last point
        if len(bv_x) > 0:
            last_x, last_y = bv_x.iloc[-1], bv_y.iloc[-1]
            if len(bv_x) >= 2:
                prev_x, prev_y = bv_x.iloc[-2], bv_y.iloc[-2]
                dx, dy = last_x - prev_x, last_y - prev_y
                angle = np.arctan2(dy, dx) if (dx != 0 or dy != 0) else 0
            else:
                angle = 0

            last_rect = plt.Rectangle((last_x - last_box_length / 2, last_y - bar_width / 2),
                                      last_box_length, bar_width,
                                      angle=np.degrees(angle),
                                      facecolor='pink', edgecolor='black',
                                      linewidth=0.9, alpha=0.9)
            ax.add_patch(last_rect)

        # Add thin black border to AV's last point
        if len(av_x) > 0:
            last_x, last_y = av_x.iloc[-1], av_y.iloc[-1]
            if len(av_x) >= 2:
                prev_x, prev_y = av_x.iloc[-2], av_y.iloc[-2]
                dx, dy = last_x - prev_x, last_y - prev_y
                angle = np.arctan2(dy, dx) if (dx != 0 or dy != 0) else 0
            else:
                angle = 0

            last_rect = plt.Rectangle((last_x - last_box_length / 2, last_y - bar_width / 2),
                                      last_box_length, bar_width,
                                      angle=np.degrees(angle),
                                      facecolor='lightblue', edgecolor='black',
                                      linewidth=0.9, alpha=0.9)
            ax.add_patch(last_rect)

        ax.set_xlabel('Lateral Position (X)')
        ax.set_ylabel('Longitudinal Position (Y)')
        ax.set_title('Vehicle Trajectories')
        ax.grid(False)
        ax.axis('equal')
        plt.show()

        return fig



