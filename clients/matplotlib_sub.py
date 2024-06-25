import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from client_sub import ClientSub
import time
import logging
from utils import get_unique_filename

# Configure logging
base_log_file = 'clients/logs/plot_update.log'
unique_log_file = get_unique_filename(base_log_file)

logging.basicConfig(
    filename=unique_log_file,  # Log to a file. Change this to None for console logging.
    level=logging.INFO,          # Log info and above levels (INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format including time
)

# Plots the data received from the subscriber in matplotlib
class MatPlotLibSub(ClientSub):
    def __init__(self, sub_ip="localhost", sub_port=1000, sub_topic="ProcessedData"):
        super().__init__(sub_ip, sub_port, sub_topic)
        self.curr_time = time.time()
        self.last_time = self.curr_time

    def update_plot(self, frame, axs, data : list = []):
        # TODO: Implement logging data
        try:
            # Measure time from the last call in milliseconds
            self.last_time = self.curr_time
            self.curr_time = time.time()
            time_since_last_plot = (self.curr_time - self.last_time) * 1000
            logging.info("Time since last plot: %.2f ms", time_since_last_plot)

            samplestamps, samples = self.get_data()

            logging.info("Received %d samples", len(samples))
            logging.debug("Samples: %s", samples)

            for i in range(self.n_channels):
                data[i].extend(samples[:,i])
                logging.info("Data successfully appended to channel data arrays")

            print("Got Data!")
        except Exception as e:
            logging.error("Failed to get data: %s", str(e))

            print("Did not get data :(")
            return  # Exit if we failed to get data
        
        line_objects = []
        for i, ax in enumerate(axs):
            ax.clear()
            ax.set_title(f"Channel {i+1}")
            line, = ax.plot(data[i][-2000:])
            ax.relim()
            ax.autoscale_view(True, True, True)
            line_objects.append(line)

        return line_objects

    def plot_data(self, n_channels : int = 1):
        self.n_channels = n_channels  # Set the number of channels you want to plot
        fig, axs = plt.subplots(self.n_channels, 1, figsize=(8, 6 * self.n_channels))

        fig.subplots_adjust(hspace=0.5)

        # Initialize empty lists to store data for each channel
        data = [[] for _ in range(self.n_channels)]

        logging.info("Starting plot with %d channels", self.n_channels)

        try:
            ani = FuncAnimation(fig, self.update_plot, fargs=(axs, data), frames=None, blit=True, interval=1, repeat=False)
            plt.show()

        except KeyboardInterrupt:
            print("Subscriber stopped by user")

if __name__ == "__main__":
    subscriber = MatPlotLibSub()
    subscriber.plot_data(2)