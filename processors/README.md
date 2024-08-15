# Processors

Folder containing the processors that can be used in conjunction with the NeuroWorks Python SDK. Specify which processor to use by adding the path of the processors folder to the `zmq-sub.py` client in the `nw-sdk-realtime` repository and using the keyword `--class ProcessorName` when running the NeuroWorks Python SDK.

## BaseZmqProcessor
Serves as the base class from which all custom processors inherit from. Allows for real-time reception of data batches and can specify what kind of batch processing one would like to implement in the `process` function.

## PublisherZmqProcessor
A processor class that receives data batches and performs some custom batch processing. Publishes data to a unique topic for ZeroMQ subscribers to receive processed data.

## UnityZmqProcessor
A processor class that receives data batches and performs some custom batch processing. Publishes data specifically for NetMQ subscribers in Unity Game Engine to receive processed data.

## PlotZmqProcessor
Experimental processor that plots the data batches directly from the data stream without needing an additional user interface (caution: does not run as quickly).