import yaml, os
import pandas as pd
from datetime import datetime
from ShellyENEA.ShellyLab import ShellyLab

__HERE__ = os.path.dirname(os.path.realpath(__file__))

def test_minimal_example():
    FILE_NAME = "Shellys.yml"
    with open(os.path.join(__HERE__, 'DATA', FILE_NAME)) as file:
        ecosystem_config = yaml.safe_load(file)
    shelly_lampedusa = ShellyLab('Lampedusa', ecosystem_config['Lampedusa'], __HERE__)
    shelly_lampedusa.start_monitoring(file_location = os.path.join(__HERE__,"PLAYGROUND"), acquisition_rate = 0.25, save_rate = 1, duration = '90 s')
    file_name = "data_shelly_Lampedusa_" + datetime.now().strftime("%Y-%m-%d")
    pd.read_csv(os.path.join(__HERE__, "PLAYGROUND", f'{file_name}.csv'), sep=";")
    assert True

def test_ESP32():
    # Test to read data from a ESP32
    FILE_NAME = 'test_ESP32_Bologna.yml'
    with open(os.path.join(__HERE__, 'DATA', FILE_NAME)) as file:
        ecosystem_config = yaml.safe_load(file)
    shelly_lampedusa = ShellyLab('Bologna', ecosystem_config['Bologna'], __HERE__)
    shelly_lampedusa.start_monitoring(file_location = os.path.join(__HERE__,"PLAYGROUND"), acquisition_rate = 0.25, save_rate = 1, duration = '90 s')
    file_name = "data_shelly_Lampedusa_" + datetime.now().strftime("%Y-%m-%d")
    print('fatto!')
    pd.read_csv(os.path.join(__HERE__, "PLAYGROUND", f'{file_name}.csv'), sep=";")
    assert True
