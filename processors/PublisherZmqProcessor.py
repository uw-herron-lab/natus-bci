import numpy as np
import time
import zmq
from zmq import Socket
import pickle
from MyZmqProcessor import MyZmqProcessor

class PublisherZmqProcessor(MyZmqProcessor):
    """Notes:
        - This file should reside in the same folder as the ZMQ subscriber
        - This class name must match the filename in order to be properly loaded by the ZMQ subscriber
        - If you wish to change the class/file name, be sure to call the subscriber with `--class YourNewName`
    """
    
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

        super().__init__(sub_ip, batch_size, info_port, event_port)

        # Setup the ZeroMQ context & publisher
        self.pub_topic = pub_topic
        self.pub_port = pub_port
        self.pub_socket: Socket = self.context.socket(zmq.PUB)
        self.setupPublisher(self.pub_socket, self.pub_port, self.pub_topic)

    def setupPublisher(self, socket: zmq.Socket, pub_port: int, pub_topic: str):
        """Bind a PUBlisher to a given port, and print PUB info

        Args:
            socket (Socket): ZeroMQ socket to publish to
            pub_port (int): port to publish to
            pub_topic (str): topic to publish to
        """
        url = "tcp://*:{}".format(pub_port)
        socket.bind(url)
        print("Publishing to topic {} on: {}".format(pub_topic, url))

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

        ### Example: Publish the data to a different topic ###

        samplestamps = np.array(samplestamps)
        samplestamps_serialized = pickle.dumps(samplestamps)

        samples = np.array(samples)
        print(samples)
        
        samples_serialized = pickle.dumps(samples)

        self.pub_socket.send_multipart([self.pub_topic.encode(), samplestamps_serialized, samples_serialized])
        print("Sent samplestamps and samples!")
                
        # measure time from the last call in milliseconds
        self.last_time = self.curr_time
        self.curr_time = time.time()
        print("Time since last call: {} ms".format((self.curr_time - self.last_time)*1000))
        print("Received batch of {} samples with {} channels".format(len(samplestamps), n_channels))