import zmq
import pickle
import struct
from zmq import Socket
import time

class ClientSub():
    def __init__(self, sub_ip: str = "localhost", sub_port: int = 6000, req_port: int = 6001, sub_topic: str = "ProcessedData"):
        """Class constructor
        Args:
            sub_ip (str, optional): IP addr of the data source. Defaults to "localhost".
            sub_port (int, optional): Port to subscribe to receive batch processed data. Defaults to 5000.
            sub_topic(str, optional): Topic to publish batch processed data. Defaults to "ProcessedData".
        """
        self.sub_ip = sub_ip
        self.sub_port = sub_port
        self.sub_topic = sub_topic
        self.req_port = req_port

        self.context: zmq.Context = zmq.Context()
        
        try:
            self.sub_socket: Socket = self.context.socket(zmq.SUB)
            self.sub_socket.connect("tcp://{}:{}".format(self.sub_ip, self.sub_port))
            self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.sub_topic)
            print(f"Connected SUB socket to tcp://{self.sub_ip}:{self.sub_port} with topic '{self.sub_topic}'")
        except Exception as e:
            print(f"Error connecting SUB socket: {e}")

        try:
            self.req_socket: Socket = self.context.socket(zmq.REQ)
            self.req_socket.connect("tcp://{}:{}".format(self.sub_ip, self.req_port))
            print(f"Connected REQ socket to tcp://{self.sub_ip}:{self.req_port}")
        except Exception as e:
            print(f"Error connecting REQ socket: {e}")
        
        self.ch_names = None

    def get_channel_names(self):
        while self.ch_names is None:
            try:
                print("Requesting channel names...")
                self.req_socket.send("get_channel_names".encode())
                ch_names = self.req_socket.recv_string()
                self.ch_names = ch_names.split('\n')
                print("Sent request!")
                # print(f"Received channel names: {self.ch_names}")
            except Exception as e:
                print(f"Error getting channel names: {e}")
                time.sleep(0.1)

    def get_data(self):
        try:
            topic, samplestamps, samples, timestamp = self.sub_socket.recv_multipart()

            samplestamps = pickle.loads(samplestamps)
            samples = pickle.loads(samples)
            timestamp = struct.unpack('d', timestamp)[0]
            
            # print(f"Received data for topic '{topic.decode()}': {data}")
            
            return samplestamps, samples, timestamp
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
    
if __name__ == "__main__":
    client = ClientSub(sub_port=1000)

    try:
        while True:
            try:
                data = client.get_data()

            except KeyboardInterrupt:
                print("Subscriber stopped by user")
                break

    finally:
        client.sub_socket.close()
        client.req_socket.close()
        client.context.term()