import numpy as np
import time
import json
from PublisherZmqProcessor import PublisherZmqProcessor

class UnityZmqProcessor(PublisherZmqProcessor):
    def __init__(self, sub_ip = "localhost", batch_size: int = 1, info_port: int = 5597, event_port: int = 5598, pub_port: int = 1000, pub_topic : str = "ProcessedData"):
        """Class constructor
        Args:
            sub_ip (str, optional): IP addr of the data source. Defaults to "localhost".
            batch_size (int, optional): Batch size to process. Defaults to 1.
            info_port (int, optional): Port to request study info from. Defaults to 5597.
            event_port (int, optional): Port to submit annotation requests. Defaults to 5598.
            pub_port (int, optional): Port to publish batch processed data. Defaults to 5000.
            pub_topic(str, optional): Topic to publish batch processed data. Defaults to "ProcessedData".
        """
        print("Initializing user-defined batch-processor")

        super().__init__(sub_ip, batch_size, info_port, event_port, pub_port, pub_topic)

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
        samples = np.array(samples)
        samples = samples[:, 0] # Just data from first channel
        data_dict = {"samples": samples.tolist()}

        samples_serialized = json.dumps(data_dict).encode()
        # print(samples_serialized)
        self.pub_socket.send_multipart([self.pub_topic.encode(), samples_serialized])
        print("Message sent!")

        self.last_time = self.curr_time
        self.curr_time = time.time()
        print("Time since last call: {} ms".format((self.curr_time - self.last_time)*1000))
        print("Received batch of {} samples with {} channels".format(len(samplestamps), n_channels))

