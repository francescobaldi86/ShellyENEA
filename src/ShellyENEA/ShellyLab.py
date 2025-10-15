import os
from datetime import datetime, timedelta
import pandas as pd
from schedule import Scheduler
from time import sleep
from ShellyENEA.Shelly import Shelly




class ShellyLab():
    """
    A class to handle a group of Shellys in the same place whose data we want to collect
    """
    def __init__(self, name, config, file_location):
        self.name = name
        self.shellys = dict()
        for shelly_name, shelly_config in config.items():
            self.shellys[shelly_name] = Shelly.create_new(shelly_config)
        self.current_time = datetime.now()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.file_location = file_location
        self.scheduler = Scheduler()

    def read_data(self, current_time = None, verbose = True):
        """
        Reads data from all Shellys of the lab
        """
        self.current_time = current_time.strftime("%Y-%m-%d %H:%M:%S") if current_time else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for shelly_name, shelly in self.shellys.items():
            shelly.read_data(current_time = self.current_time)
        if verbose:
            print(f'Reading data from Shelly lab {self.name} at {self.current_time}')
            
    def erase_data(self):
        """
        Erases the stored data from all Shellys that belong to the ShellyLab
        """
        for shelly_name, shelly in self.shellys.items():
            shelly.erase_data()

    def export_data(self, file_location = None, file_name = None, change_name_every_day = True, verbose = True):
        """
        Allows exporting the data to a .csv file
        """
        if file_location is None:
            file_location = self.file_location
        if file_name is None:
            file_name = 'Shelly_data'
        if change_name_every_day:
            file_name = f'{file_name}_{datetime.now().strftime("%Y-%m-%d")}'  # The filename is updated usi>
            if datetime.now().strftime("%Y-%m-%d") != self.current_date:
                self.erase_data()                                # If the current date is different from th>
        # Create multi-index
        multi_index = [[],[]]
        for shelly_name, shelly in self.shellys.items():
            index = shelly.data.index
            for column in shelly.data.columns:
                multi_index[0].append(shelly_name)
                multi_index[1].append(column)
        data = pd.DataFrame(columns = pd.MultiIndex.from_tuples(list(zip(*multi_index)), names=["shelly", "variable"]), index=index)
        for shelly_name, shelly in self.shellys.items():
            for column in shelly.data.columns:
                data.loc[:,(shelly_name, column)] = shelly.data.loc[:, column]
        data.to_csv(os.path.join(file_location, f'{file_name}.csv'), sep=";")
        self.current_date = datetime.now().strftime("%Y-%m-%d")  # Updates current date
        if verbose:
            print(f'Saving data from Shelly lab {self.name} at {file_location} on {file_name}')

    def start_monitoring(self, 
                              acquisition_rate = 1, 
                              save_rate = 10,
                              duration = 10,
                              file_location = None,
                              file_name = None,
                              change_name_every_day = True):
        """
        function that activates the data monitoring from the shellys of the lab
        :param: acquisition_rate    Data is acquired every "acquisition_rate" minutes
        :param: save_rate           Data is saved every "save_rate" minutes
        :param: file_location       Directory where to save the data. If left blank, uses the base directory
        :param: file_name           Name of the file where to save the data. If not provided, uses "Shelly_data"
        :param: change_name_every_day    If true, changes the name of the file every day. If false, it always uses the same name
        """
        print('Start monitoring Shelly lab', self.name)
        print('Data will be saved to', file_location)
        file_name = f'data_shelly_{self.name}'
        [value, unit] = duration.split(' ')
        match unit:
            case 's' | 'secs' | 'seconds':
                end_monitoring = datetime.now() + timedelta(seconds = float(value))
            case 'm' | 'min' | 'mins' | 'minutes':
                end_monitoring = datetime.now() + timedelta(minutes = float(value))
            case 'h' | 'hours':
                end_monitoring = datetime.now() + timedelta(hours = float(value))
            case 'min' | 'm':
                end_monitoring = datetime.now() + timedelta(minutes = float(value))
            case 'd' | 'days': 
                end_monitoring = datetime.now() + timedelta(days = float(value))
        # Read data from the Shellys every READ_DATA_INTERVAL seconds
        self.scheduler.every(acquisition_rate).minutes.do(self.read_data)
        # Every X timers, save the data to a CSV file
        if file_location:
            data_files_directory = file_location
        else:
            data_files_directory = self.file_location
        self.scheduler.every(save_rate).minutes.do(self.export_data, file_location = data_files_directory, file_name = file_name)
        while self.current_time <= end_monitoring:
            self.scheduler.run_pending()
            sleep(1)
            self.current_time = datetime.now()


class ShellyEnvironment():
    """
    A class to handle more than one shelly lab
    """
    def __init__(self, config):
        self.labs = {}
        for lab_name, lab_content in config.items():
            self.labs[lab_name] = ShellyLab(config=lab_content)
