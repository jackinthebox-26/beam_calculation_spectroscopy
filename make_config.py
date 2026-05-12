"""
This file creates the configuration files for the optical elements.

This has to be loaded once as it creates the json files for the subsequest calculations.



"""
# Standard library imports
import os
import json

# Other public imports
import numpy as np
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

def initiate_thorlabs_UM10_Y4HP_turning_mirror():
    data = {'name': 'Thorlabs UV turning mirror UM10-Y4HP',
            'filename': 'turning_mirror_thorlabs_UM10_Y4HP.json',
            'type': 'mirror'}
    make_configfile(data)


def initiate_tower_QWP():
    data = {'name': 'Tower optical quarter wave plate',
            'filename': 'tower_optical_qwp.json',
            'width': 1e-3}
    make_configfile(data)

def initiate_data():
    """This method creates the relevant config files."""
    logger.info('Begining config initiation')
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



def make_json_files():
    initiate_data()
    initiate_thorlabs_100_mm_convex_UV_LA4380()
    initiate_thorlabs_UM10_Y4HP_turning_mirror()
    initiate_tower_QWP()

def main():
    make_json_files()
if __name__ == "__main__":
    main()
