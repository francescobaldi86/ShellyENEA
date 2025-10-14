import yaml, os
import pandas as pd
from ShellyENEA.ShellyLab import ShellyLab

__HERE__ = os.path.dirname(os.path.realpath(__file__))

def test_minimal_example():
  
    FILE_NAME = "Shellys.yaml"
    with open(os.path.join(__HERE__, FILE_NAME)) as file:
        ecosystem_config = yaml.safe_load(file)
    shelly_lampedusa = ShellyLab('Lampedusa', ecosystem_config['Lampedusa'], __HERE__)
    shelly_lampedusa.start_monitoring(file_location = os.path.join(__HERE__,"PLAYGROUND"), acquisition_rate = 0.5, save_rate = 15, duration = '20 s')
    file_name = file_name + "_" + datetime.now().strftime("%Y-%m-%d")
    pd.read_csv(os.path.join(__HERE__, "PLAYGROUND", f'{file_name}.csv'), sep=";")