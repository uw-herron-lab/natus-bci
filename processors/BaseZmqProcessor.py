import json
import numpy as np
import time
import zmq
from zmq import Socket

class BaseZmqProcessor():    
    def __init__(self, sub_ip = "localhost", batch_size: int = 1, info_port: int = 5597, event_port: int = 5598):
        """Class constructor
        Args:
            sub_ip (str, optional): IP addr of the data source. Defaults to "localhost".
            batch_size (int, optional): Batch size to process. Defaults to 1.
            info_port (int, optional): Port to request study info from. Defaults to 5597.
            event_port (int, optional): Port to submit annotation requests. Defaults to 5598.
        """
        print("Initializing user-defined batch-processor")
        
        self.sub_ip = sub_ip
        self.info_port = info_port
        self.event_port = event_port
        
        # setup info socket
        self.context: zmq.Context = zmq.Context()
        self.info_socket: Socket  = self.create_request_socket(self.context, "tcp://{}:{}".format(self.sub_ip, self.info_port)) # for requesting study info
        self.event_socket: Socket = self.create_request_socket(self.context, "tcp://{}:{}".format(self.sub_ip, self.event_port)) # for submitting annotations
        self.batch_size = batch_size
        self.curr_time = time.time()
        self.last_time = self.curr_time

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
        
        # measure time from the last call in milliseconds
        self.last_time = self.curr_time
        self.curr_time = time.time()
        print("Time since last call: {} ms".format((self.curr_time - self.last_time)*1000))
        print("Received batch of {} samples with {} channels".format(len(samplestamps), n_channels))
        
    def request_info(self, socket, msg: str = "info please") -> dict:
        '''Function for requesting info via a REQ/REP socket'''
        socket.send_string(msg)
        return json.loads(socket.recv_string())
    
    def request_create_annotation(self, socket: Socket, samplestamp: str, msg: str = "some annotation...") -> dict:
        '''Request a generic annotation be created in the NeuroWorks study; REQ/REP socket'''
        socket.send_string(str(samplestamp), zmq.SNDMORE)
        socket.send_string(msg)
        return socket.recv_string()

    def create_request_socket(self, context: zmq.Context, connectionString: str) -> Socket:
        socket: Socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.REQ_RELAXED, 1)
        socket.setsockopt(zmq.REQ_CORRELATE, 1)
        socket.connect(connectionString)
        socket.RCVTIMEO = 2000
        socket.SNDTIMEO = 2000
        print("Created REQ socket: {}".format(connectionString))
        return socket
