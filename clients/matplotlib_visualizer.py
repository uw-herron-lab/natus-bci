import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from client_sub import ClientSub
import time
import logging
import json
from utils import get_unique_filename, setup_logging, time_to_float
import numpy as np

# Define constants for file paths
DEBUG_LOG_FILE = 'clients/logs/matplotlib_visualizer/debug.log'
DATA_LOG_FILE = 'clients/logs/matplotlib_visualizer/data.json'

# Setup logging
setup_logging(DEBUG_LOG_FILE)

# Plots the data received from the subscriber in matplotlib
class MatPlotLibViz(ClientSub):
    def __init__(self, sub_ip="localhost", sub_port=1000, sub_topic="ProcessedData"):
        super().__init__(sub_ip, sub_port, sub_topic)
        self.curr_time = time.time()
        self.last_time = self.curr_time
        self.data_log = {"samplestamps": []}

    def update_plot(self, frame, axs):
        try:
            samplestamps, samples, timestamp = self.get_data()

            logging.info("Received %d samples", len(samples))
            self.data_log["samplestamps"].extend(samplestamps)
            
            # Measure time from the last call in milliseconds
            self.last_time = self.curr_time
            self.curr_time = time.time()
            
            time_since_last_plot = (self.curr_time - self.last_time) * 1000
            logging.info("Time since last plot: %.2f ms", time_since_last_plot)

            time_since_last_data = (self.curr_time - timestamp) * 1000
            # logging.info("Current time: %f ms", self.curr_time)
            # logging.info("Timestamp: %f ms", timestamp)
            logging.info("Time to receive batch data from first subscriber: %f ms", time_since_last_data)

            for i in range(self.n_channels):
                self.data_log[f"channel_{i+1}"].extend(samples[:, i])
                logging.info(f"Data successfully appended to channel {i+1}")

            print("Got Data!")
        except Exception as e:
            logging.error("Failed to get data: %s", str(e))

            print("Did not get data :(")
            return  # Exit if we failed to get data
        
        line_objects = []
        for i, ax in enumerate(axs):
            ax.clear()
            ax.set_title(f"Channel {i+1}")
            line, = ax.plot(self.data_log[f"channel_{i+1}"][-2000:])
            ax.relim()
            ax.autoscale_view(True, True, True)
            line_objects.append(line)

        return line_objects

    def plot_data(self, n_channels : int = 1):
        self.n_channels = n_channels  # Set the number of channels you want to plot
        for i in range(self.n_channels):
            self.data_log[f"channel_{i+1}"] = []

        fig, axs = plt.subplots(self.n_channels, 1, figsize=(8, 6 * self.n_channels))
        fig.subplots_adjust(hspace=0.5)
        logging.info("Starting plot with %d channels", self.n_channels)

        try:
            ani = FuncAnimation(fig, self.update_plot, fargs=(axs,), frames=None, blit=True, interval=1, repeat=False)
            plt.show()

        except KeyboardInterrupt:
            print("Subscriber stopped by user")

        self.save_data_log()

    def save_data_log(self):
        unique_data_log_file = get_unique_filename(DATA_LOG_FILE)

        with open(unique_data_log_file, "w") as json_file:
            for key in self.data_log.keys():
                self.data_log[key] = np.array(self.data_log[key])
                if isinstance(self.data_log[key], np.ndarray):
                    self.data_log[key] = self.data_log[key].tolist()
            json.dump(self.data_log, json_file, indent=4)
        logging.info("Data log saved to %s", unique_data_log_file)

if __name__ == "__main__":
    subscriber = MatPlotLibViz()
    subscriber.plot_data(2)