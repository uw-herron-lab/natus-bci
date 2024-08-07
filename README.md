# Realtime EEG Data Streaming and Processing With Natus Python SDK

These scripts are complementary to the `nw-sdk-realtime` repository, to obtain an NDA with Natus Medical, Inc., please contact Natus Medical, Inc. at [sdk@natus.com] along with your name, title, entity/institution and email address. 

This repository is divided into two folders:

- processors
  - handles all the batch preprocessing of data
  - tells the first client what to do with the processed data
- clients
  -  a second client that receives processed data
  -  visualizes data via a user interface, creates a BCI task, etc.
 
To utilize processors in this repository, you must add the `natus-bci/processors` folder path to the `nw-sdk-realtime/NeuroWorksDataClients/python/zmq-sub.py` Python file found in the `nw-sdk-realtime` repository.

```Python
  # zmq-sub.py
  import sys 
  path_to_processors = "path/to/processors" 
  sys.path.append(path_to_processors)
```

Then proceed to follow the documentation in the `nw-sdk-realtime` repository to select which processor class you would like to use (designated by specifying the `--class` keyword in the terminal). Clients in the `clients` folder can be ran independently in a different terminal.
