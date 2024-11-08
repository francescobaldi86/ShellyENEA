import requests, json, yaml
from datetime import datetime
import pandas as pd
from importlib import resources as impresources
import data

base_shelly_data = impresources.files(data) / 'shelly_data_config.yaml'
with open(base_shelly_data) as file:
    BASE_CONFIG = yaml.safe_load(file)


class Shelly:
    """
    Generic class defining a single shelly
    """
    def __init__(self, config):
        Shelly.verify_config_file(config)
        self.config = config
        self.ip = config["ip"]
        self.mac_address = config['mac_address']
        self.location = config["location"]
        self.type = config["type"]
        self.data = pd.DataFrame()
        self.current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.gen = BASE_CONFIG[self.type]['gen']
        self.config_addon(config)
        self.config_shelly_data()

    def config_shelly_data(self):
        """
        Basic Shelly configuration
        """
        self.vars = {}
        for var_info in BASE_CONFIG[self.type]['vars']:
            try:
                name = f'{var_info["unit"]}:{self.config[var_info["custom_name_field"]]}'.rstrip(":")
            except KeyError:
                name = f'{var_info["unit"]}:{var_info["default_name"]}'.rstrip(":")
            self.vars[name] = var_info['location']

    def config_addon(self, config):
        """
        Adds the information about the addon
        """
        if 'addon' not in config.keys():
            self.addon = None
        else:
            self.addon = AddOn(config['addon'])

    def read_data(self, current_time = None):
        """
        Reads data from the Shelly EM
        """
        match self.gen:
            case 1:
                url = f"http://{self.ip}/status"
            case 2:
                url = f"http://{self.ip}/rpc/Shelly.GetStatus"
        temp = Shelly.send_request(url)
        self.current_time = current_time if current_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            for var_name, var_location in self.vars.items():
                self.data.loc[self.current_time, var_name] = Shelly.read_from_field(temp, var_location)
            # Read also data from the addon
            if self.addon:
                self.data = self.data.combine_first(self.addon.read_data(temp, self.current_time))
        except (ValueError, TypeError):
            print(f"Could not read data at time {current_time} for Shelly {self.type}")
            
            
    def erase_data(self):
        """
        Erases all the data in the Shelly, and re-initializes the "data" field
        """
        self.data = pd.DataFrame()


    @staticmethod
    def create_new(config):
        """
        Used to create a new shelly of the right type
        """
        match config["type"]:
            case "EM":
                return Shelly_EM(config)
            case "1PM":
                return Shelly_1PM(config)
            case "RGBW2":
                return Shelly_RGBW2(config)
            case "Dimmer":
                return Shelly_Dimmer(config)
            case "1Plus":
                return Shelly_1Plus(config)

    
    @staticmethod
    def verify_config_file(config):
        """
        Verifies that the config file is appropriately defined
        """
        # Verify format of the IP address
        # Verify format of the mac address
        # Verify that "location" is string
        # Verify that "type" is within accepted list
        # Verify that "has_addon" is boolean
        # Verify that "addon" exists and is a dict if has_addon is true
        # Emit warning if "addon" exists but has_addon is false
 
    @staticmethod
    def send_request(url):
        """
        Sends the http request to the shelly given the correct IP address and url request
        """
        try:
            response = requests.get(url)  #, data=body_data
        except Exception as error:
            print('Error:', error)
            return
        if response.status_code != 200:
            print(f"Error in the request: {response.status_code} - {response.text}", '  with request ', url)
            return
        jsondata = json.loads(response.text)
        return jsondata

    @staticmethod
    def read_from_field(data, location):
        location = location.split("_")
        for position, id in enumerate(location):
            if location[position].isdigit():
                location[position] = int(id)
        # Note: multiplying by 1 allows converting booleans to int, thus avoiding pandas warning messages
        if len(location) == 1:
            return data[location[0]] * 1  
        elif len(location) == 2:
            return data[location[0]][location[1]] * 1
        elif len(location) == 3:
            return data[location[0]][location[1]][location[2]] * 1
        else:
            raise KeyError('The lenght of the location field should be at most 3')

        


class Shelly_EM(Shelly):
    """
    Extends the Shelly class to handle a Shelly EM device
    """
    def __init__(self, config):
        super().__init__(config)

class Shelly_1PM(Shelly):
    """
    Extends the Shelly class to handle a Shelly 1PM device
    """
    def __init__(self, config):
        super().__init__(config)
        
class Shelly_Dimmer(Shelly):
    """
    Reads data from a Shelly Dimmer 0-10 V
    """
    def __init__(self, config):
        super().__init__(config)

class Shelly_RGBW2(Shelly):
    """
    Class that is used to handle a Shelly RGBW-2 unit
    """
    def __init__(self, config):
        super().__init__(config)
        
class Shelly_1Plus(Shelly):
    """
    Extends the Shelly class to handle a Shelly 1PM device
    """
    def __init__(self, config):
        super().__init__(config)
        

class AddOn():
    """
    Class to handle Shelly addons
    """
    def __init__(self, config):
        self.channels = []
        for channel in config['channels']:
            self.channels.append(channel)
    
    def read_data(self, temp, current_time):
        data = pd.DataFrame(index = [current_time])
        for channel in self.channels:
            if channel['type'] == 'Temperature':
                data.loc[current_time, f"Temperature:{channel['name']}"] = temp[f'temperature:{channel["id"]}']['tC']
            if channel['type'] == 'Current':
                data.loc[current_time, f"Current:{channel['name']}"] = temp[f'voltmeter:{channel["id"]}']['voltage']
        return data