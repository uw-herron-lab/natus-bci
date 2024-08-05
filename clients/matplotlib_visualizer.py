import time
import logging
import csv
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from client_sub import ClientSub
from utils import get_unique_filename, setup_logging

# Define constants for file paths
DATA_LOG_FILE = 'logs/matplotlib_visualizer/data.csv'
DEBUG_LOG_FILE = 'logs/matplotlib_visualizer/debug.log'

# Setup logging
setup_logging(DEBUG_LOG_FILE)

# Plots the data received from the subscriber in matplotlib


class MatPlotLibViz(ClientSub):
    def __init__(self, sub_ip="localhost", sub_port=6000, req_port=6001,
                 sub_topic="ProcessedData"):
        super().__init__(sub_ip, sub_port, req_port, sub_topic)
        self.curr_time = time.time()
        self.last_time = self.curr_time
        self.ch_data = {}
        self.lines = []
        self.queue = queue.Queue()

        self.get_channel_names()

    def update_plot(self, frame, ax, sep, win_size):
        try:
            start_get_data_time = time.time()
            samplestamps, samples, timestamp = self.get_data()
            end_get_data_time = time.time()

            data_log = {}

            logging.info("Received %d samples", len(samples))
            data_log["samplestamps"] = samplestamps

            logging.info("Time it takes to pull data: %f ms",
                         end_get_data_time - start_get_data_time)

            # Measure time from the last call in milliseconds
            self.last_time = self.curr_time
            self.curr_time = time.time()

            time_since_last_plot = (self.curr_time - self.last_time) * 1000
            logging.info("Total time since previous plot iteration: %.2f ms",
                         time_since_last_plot)

            time_since_last_data = (self.curr_time - timestamp) * 1000
            logging.info("Time delay between first and second subscriber: %f ms",
                         time_since_last_data)

            if samples.shape[1] < self.n_channels:
                raise ValueError("Trying to plot more channels than there are in the data")

            start_plot_data_time = time.time()
            for i in range(self.n_channels):
                data_log[self.ch_names[i]] = samples[:, i]
                self.ch_data[self.ch_names[i]].extend(samples[:, i] + i*sep)
                # logging.info(f"Data successfully appended to {self.ch_names[i]}")

                # Limit window size
                if len(self.ch_data[self.ch_names[i]]) > win_size:
                    del self.ch_data[self.ch_names[i]][:len(self.ch_names[i]) - win_size]

                self.lines[i].set_ydata(self.ch_data[self.ch_names[i]])
                self.lines[i].set_xdata(range(len(self.ch_data[self.ch_names[i]])))

            ax.relim()
            ax.autoscale_view(True, True, True)
            ax.legend()
            ax.tick_params(axis='y', labelleft=False)
            ax.set_xlabel("Samples")
            ax.set_ylabel("Amplitude")

            end_plot_data_time = time.time()

            logging.info("Time it takes to plot data: %f ms",
                         end_plot_data_time - start_plot_data_time)

            self.queue.put(data_log)
            print("Got Data!")

            return self.lines

        except Exception as e:
            logging.error("Failed to get data: %s", str(e))
            print("Did not get data :(")
            return  # Exit if we failed to get data

    def plot_data(self,
                  n_channels: int = 1,
                  sep: float = 0,
                  win_size: int = 2000):
        self.n_channels = n_channels  # Set the number of channels you want to plot
        for i in range(self.n_channels):
            self.ch_data[self.ch_names[i]] = []

        fig, ax = plt.subplots(figsize=(8, 6 * self.n_channels))

        logging.info("Starting plot with %d channels", self.n_channels)

        try:
            for i in range(self.n_channels):
                line, = ax.plot([], [], label=self.ch_names[i])
                self.lines.append(line)

            ani = FuncAnimation(fig, self.update_plot, fargs=(ax, sep, win_size),
                                frames=None, blit=True, interval=1, repeat=False)
            plt.show()

        except Exception as e:
            logging.error("Plotting error: %s", str(e))
            print("Subscriber stopped by user")

        self.save_data_log()

    def save_data_log(self):
        csv_file = get_unique_filename(DATA_LOG_FILE)

        with open(csv_file, "w", newline='') as file:
            fieldnames = ["samplestamps"]
            fieldnames.extend(self.ch_names[:self.n_channels])

            # Create a CSV DictWriter object
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            while True:
                data = self.queue.get()
                if data is None:
                    break

                num_rows = len(next(iter(data.values())))
                for i in range(num_rows):
                    row = {key: value[i] for key, value in data.items()}
                    writer.writerow(row)

                self.queue.task_done()


if __name__ == "__main__":
    visualizer = MatPlotLibViz()

    writer_thread = threading.Thread(target=visualizer.save_data_log)
    writer_thread.start()

    try:
        visualizer.plot_data(n_channels=8, sep=1e-4, win_size=2000)
    finally:
        visualizer.queue.put(None)  # Signal the writer thread to exit
        writer_thread.join()
