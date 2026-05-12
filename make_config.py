"""
This file creates the configuration files for the optical elements.
"""

import os
import numpy as np
import json
from loguru import logger

CONFIG_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'config')

def make_configfile(config):

    """This method creates a config file from a config dictionary."""
    logger.info(f'    Creating {config["name"]} config')
    file = config['filename']
    with open(CONFIG_FOLDER + file, 'w') as f:
        json.dump(config, f, indent=4)
    logger.info(f'    Done creating {config["name"]} config')

def initiate_thorlabs_100_mm_convex_UV_LA4380():
    logger.info('Begining thorlabs config')
    lens_thorlabs_LA4380_UV = {'name': 'Thorlabs 100 mm Convex UV LA4380',
                               'filename': 'config_lens_thorlabs_LA4380_UV.json',
                               'type': 'lens',
                               'focal_length': 100e-3,  # m
                               'width': 2.6e-3,  # m
                               'transmission': 0.95,  # 
                               'index': 1.458,  # 
                               'aperture': 5.4e-3,  # m
                               'GVD': 36e-27 # s^2/m
                                }
    make_configfile(lens_thorlabs_LA4380_UV)
    logger.info('Done thorlabs config.')

def initiate_data():
    """This method creates the relevant config files."""
    logger.info('Begining config initiation')
    folder = '../config/'
    coll_lens = {'name': 'collimating lens',
                 'filename': 'config_coll_lens.json',
                 'type': 'lens',
                 'focal_length': 1.1,
                 'width': 2e-3}

    qwp = {'name': 'Quarterwave Plate',
           'filename': 'config_qwp.json',
           'type': 'qwp',
           'angle': 2*np.pi/7,
           'width': 2e-3}

    pbc = {'name': 'Polarizing Beam Cube',
           'filename': 'config_pbc.json',
           'type': 'pbc',
           'arm': 'T',
           'width': 0.25,
           'GVD': 214.83e-27}

    hwp = {'name': 'Halfwave Plate',
           'filename': 'config_hwp.json',
           'type': 'hwp',
           'angle': np.pi/7,
           'width': 2e-3}

    beam_shape_lens_1 = {'name': 'Beam Shape lens 1',
                         'filename': 'config_shape_lens_1.json',
                         'type': 'lens',
                         'focal_length': 100e-3,
                         'width': 2e-3}


    configs_to_make = (coll_lens, beam_shape_lens_1, qwp, pbc, hwp)
    for config in configs_to_make:
        make_configfile(config)

    logger.info('Done creating config')

def main():
    initiate_data()
    initiate_thorlabs_100_mm_convex_UV_LA4380()
    with open('../config/config_qwp.json', 'r') as f:
        data = json.load(f)
if __name__ == "__main__":
    main()
