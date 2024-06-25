import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import queue
from MyZmqProcessor import MyZmqProcessor

class PlotZmqProcessor(MyZmqProcessor):
    def __init__(self, sub_ip="localhost", batch_size=1, info_port=5597, event_port=5598):
        print("Initializing user-defined batch-processor")

        super().__init__(sub_ip, batch_size, info_port, event_port)
        
        # Data storage and queue for thread-safe sharing
        self.data_queue = queue.Queue()
        
        # Thread for plotting
        self.plot_thread = threading.Thread(target=self.plot_data, args=(2,))
        self.plot_thread.start()
    
    def update_plot(self, frame, axs: plt.Axes):
        # Create a line object
        # line, = axs.plot([], [])
        line_objects = []
        
        # Update the plot with data from the queue
        while not self.data_queue.empty():
            new_samples = self.data_queue.get_nowait()
            for ch in range(self.n_channels):
                self.data[ch].extend(new_samples[:, ch])
                self.data[ch] = self.data[ch][-2000:]  # Keep only the last 2000 samples
        
        for i, ax in enumerate(axs):
            ax.clear()
            ax.set_title(f"Channel {i+1}")
            line, = ax.plot(self.data[i])
            ax.relim()
            ax.autoscale_view(True, True, True)
            line_objects.append(line)

        return line_objects
    
    def plot_data(self, n_channels : int = 2):
        self.n_channels = n_channels  # Set the number of channels you want to plot

        fig, axs = plt.subplots(self.n_channels, 1, figsize=(8, 6 * self.n_channels))

        fig.subplots_adjust(hspace=0.5)

        # Initialize empty lists to store data for each channel
        self.data = [[] for _ in range(self.n_channels)]
        
        # Setup FuncAnimation for real-time updates
        ani = FuncAnimation(fig, self.update_plot, fargs=(axs,), interval=100, blit=False, repeat=False)
        
        plt.show()
    
    def process(self, n_channels, samplestamps, samples):
        """This function will receive `M x N` array of sample data
            - M is defined by the `--batch` argument provided to `python zmq-sub.py` (see -h for defaults)
            - N is defined by the `--channels` argument provided to `python zmq-sub.py` (see -h, default is to receive all channels)
            - E.g. To receive batches with 1k samples, each with 2 channel values, run `python zmq-sub.py --batch 1000 --channels 0 1`
                - Note that subscribing to the first 2 channels requires the PUBLISHER to be SENDING at least 2 channels
        Args:
            n_channels (int): the number of channels per sample sent by the publisher (for each zmq message)
            samplestamps([1D array]): array of batch_size items, each item is a samplestamp
            samples ([2D array]): array of batch_size items, each item (sample) is an array of channel data
        """
        ###################################
        # YOUR BATCH PROCESSING GOES HERE #
        ###################################
        self.data_queue.put(np.asarray(samples))
        
        # measure time from the last call in milliseconds
        self.last_time = self.curr_time
        self.curr_time = time.time()
        print("Time since last call: {} ms".format((self.curr_time - self.last_time)*1000))
        print("Received batch of {} samples with {} channels".format(len(samplestamps), n_channels))