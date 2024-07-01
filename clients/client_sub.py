import zmq
import pickle
import struct

class ClientSub():
    def __init__(self, sub_ip="localhost", sub_port=1000, sub_topic="ProcessedData"):
        """Class constructor
        Args:
            sub_ip (str, optional): IP addr of the data source. Defaults to "localhost".
            sub_port (int, optional): Port to subscribe to receive batch processed data. Defaults to 5000.
            sub_topic(str, optional): Topic to publish batch processed data. Defaults to "ProcessedData".
        """
        self.sub_ip = sub_ip
        self.sub_port = sub_port
        self.sub_topic = sub_topic
        self.context = zmq.Context()
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect("tcp://{}:{}".format(self.sub_ip, self.sub_port))
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, self.sub_topic)

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
        client.context.term()