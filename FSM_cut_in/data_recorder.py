"""A data recording tool used to capture vehicle interaction data during cut-in events."""

class DataRecorder:
    def __init__(self, testing_writer):
        self.testing_writer = testing_writer

    def init_testing_log(self):
        self.testing_writer.writerow([
            "episode", "step", "bv_x", "bv_y", "bv_speed", "bv_heading", "bv_acceleration", "bv_steering",
            "av_x", "av_y", "av_speed", "ttc_lon", "crash", "distance"
        ])

    def record_testing_data(self, episode, step, bv_x, bv_y, bv_speed, bv_heading, bv_acceleration, bv_steering,
                            av_x, av_y, av_speed, ttc_lon, crash, distance):
        self.testing_writer.writerow([
            episode, step, bv_x, bv_y, bv_speed, bv_heading, bv_acceleration, bv_steering, av_x, av_y, av_speed,
            ttc_lon, crash, distance
        ])
