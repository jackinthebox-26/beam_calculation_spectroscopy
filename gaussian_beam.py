""" TODO
Complete docs
Break plotting into seperate file
Turn this file into database creation
optical setup in json or other config file

Verify calculatoins while implementing test cases.


"""


# Standard library imports
import json
from dataclasses import dataclass

from loguru import logger

# Open source library imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Custom library imports
from make_config import initiate_data
from gaussian_beam_slice import gaussian_beam
from optical_element_objects import Lens, QWP, HWP, PBC, Space



@dataclass
class optical_layout:
    """This class runes through a particular optical layout and creates a database for future analysis."""
    init_beam: gaussian_beam  # This is the beam at the point it enters the optical setup
    element_set: tuple  # This contains two types of elements, either an optical component or a number indicating a distance
    def __post_init__(self):
        self.df = self.init_df()
        self.row_calcs()
    
    def init_df(self):
        """This method initiates the dataframe from the element set. """
        logger.info('Begin intiating dataframe.')
        dz = []
        for index, element in enumerate(self.element_set):
            if isinstance(element, (int, float)):
                dz.append(element)
            else:
                dz.append(element.width)
        z = []
        for i, new_z in enumerate(dz):
            if i == 0:
                z.append(new_z)
            else:
                z.append(z[i-1] + new_z)
        df = pd.DataFrame({'z': z, 'dz': dz, 'element': self.element_set})  
        logger.info('Finished initiating dataframe.')
        return df

    def row_calcs(self):
        """Calculate all the rows."""
        first_beam = self.init_beam
        logger.info('Begin row calculations')
        self.df.at[0, 'init_beam_profile'] = first_beam
        self.df['final_pol_vec'] = None
        self.df['init_pol_vec'] = None
        for index, row in self.df.iterrows():
            elem = row['element']
            old_beam = self.df.at[index, 'init_beam_profile']

            if isinstance(elem, (int, float)):
                new_beam = old_beam.pass_free_space(elem)
            else:
                new_beam = old_beam.pass_element(elem)

            self.df.at[index, 'final_beam_profile'] = new_beam
            if index < len(self.df.index) - 1:
                self.df.at[index+1, 'init_beam_profile'] = new_beam

            self.df.at[index, 'final_pol_vec'] = new_beam.vec
            self.df.at[index, 'init_pol_vec'] = old_beam.vec

            self.df.at[index, 'w_z_final'] = new_beam.w_z
            self.df.at[index, 'w_z_start'] = old_beam.w_z


            self.df.at[index, 'power_avg_final'] = new_beam.power_avg
        logger.info('Finished row calculations')
                
def scatter_color(df):
    vec = df.final_pol_vec
    out_color = []
    for index in range(len(df.index)):
        vec = df.at[index, 'final_pol_vec']
        a = abs(vec[0, 0])**2
        b = abs(vec[1, 0]) ** 2
        out_color.append( (a, 0, b))
    return out_color

def plot_optical_layout(ol, size_scale=100):
    fig, ax = plt.subplots()
    ax.scatter(ol.df.z, ol.df.w_z_final * 1e3, 
               c=scatter_color(ol.df),
               s=ol.df.power_avg_final * size_scale)
    ax.set_xlabel('Beam distance (m)')
    #ax.set_yscale('log')
    ax.set_ylabel('Spot size (mm)')
    ax.grid(True)
    plt.show()

def sim_setup():
    initiate_data()
    folder = '../config/'
    
    space_0_2 = Space(0.2)
    coll_lens = Lens(folder + 'config_coll_lens.json')
    qwp = QWP(folder + 'config_qwp.json')
    pbc = PBC(folder + 'config_pbc.json')
    hwp = HWP(folder + 'config_hwp.json')
    shape_lens_1 = Lens(folder + 'config_shape_lens_1.json')
    element_set = ( hwp,space_0_2,pbc,space_0_2,  qwp,space_0_2,shape_lens_1,space_0_2, shape_lens_1 , space_0_2)

    gauss = gaussian_beam(256e-9, 10e-9, 1, 0.1e-3)


    ol = optical_layout(gauss, element_set)

    plot_optical_layout(ol)


def main():

    from my_logging import configure_logging
    configure_logging()
    logger.info('Running gaussian_beam.py as __main__')
    sim_setup()
if __name__ == '__main__':
    main()
