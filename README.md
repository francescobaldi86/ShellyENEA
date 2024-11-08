# ShellyENEA
Python project to read data and manage sets of Shelly devices

## Modules

### Shelly
The Shelly module contains the main "Shelly" class that represents a single Shelly device. Further classes are defined to handle individual Shelly models (such as 1PM, EM, Dimmer, etc)

### ShellyLab
The ShellyLab module contains the ShellyLab class, whose main purpose is to include several different Shelly devices and monitor them together. 
To initialize a ShellyLab class, you need to provide:
- The name of the lab (the one you prefer!)
- A dictionary containing the information about the Shellys in the lab. The dictionary is provided as a dictionary of dictionaries, where each dictionary is a Shelly device. For each device, you need to provide ip address, device type
- The path where you want data monitoring to be saved.

## Minimal example
```
import os, yaml
from ShellyLab import ShellyLab

FILE_LOCATION = os.path.dirname(os.path.realpath(__file__))  # The yaml file containing the information about the Shelly devices is in the same folder as the Python code
FILE_NAME = "Shellys.yaml" 
with open(os.path.join(FILE_LOCATION, FILE_NAME)) as file:
    ecosystem_config = yaml.safe_load(file)
shelly_lampedusa = ShellyLab('MyShellyLab', ecosystem_config['MyShellyLab'], FILE_LOCATION)  # Creating the ShellyLab environment
shelly_lampedusa.start_monitoring(file_location = os.path.join(FILE_LOCATION, "Data"), acquisition_rate = 2/60, save_rate = 15)  # Starting monitoring the Shellys, with an acquisition frequency of 1 reading every 2 seconds, saving the file every 15 minutes
```
