""" TODO
Complete docs
optical setup in json or other config file

Verify calculatoins while implementing test cases.

Add optical elements to plots

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


def gauss_envelope(w_0, z_from_w_0, wavelength_center, index = 1):
    z_R = np.pi * w_0 ** 2 * index / wavelength_center
    return w_0 * np.sqrt(1 + (z_from_w_0 / z_R)**2)

@dataclass
class optical_layout:
    """This class runes through a particular optical layout and creates a database for future analysis."""
    init_beam: gaussian_beam  # This is the beam at the point it enters the optical setup
    element_set: tuple  # This contains two types of elements, either an optical component or a number indicating a distance
    def __post_init__(self):
        self.df = self.init_df()
        self.row_calcs()
        self.make_flat_df()
    
    def init_df(self):
        """This method initiates the dataframe from the element set. """
        logger.info('Begin intiating dataframe.')
        dz = []
        for index, element in enumerate(self.element_set):
            dz.append(element.width)
        z = [0]
        logger.info(f'{dz=}')
        for i, new_z in enumerate(dz):
            z.append(z[i] + new_z)
        z.pop()
        logger.info(f'{z=}')
        df = pd.DataFrame({'z': z, 'element': self.element_set})  
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

            new_beam = old_beam.pass_element(elem)

            self.df.at[index, 'final_beam_profile'] = new_beam
            if index < len(self.df.index) - 1:
                self.df.at[index+1, 'init_beam_profile'] = new_beam

            self.df.at[index, 'final_pol_vec'] = new_beam.vec
            self.df.at[index, 'init_pol_vec'] = old_beam.vec

            self.df.at[index, 'w_z_final'] = new_beam.w_z
            self.df.at[index, 'w_z_start'] = old_beam.w_z

            self.df.at[index, 'tau_fwhm_init'] = old_beam.tau_fwhm
            self.df.at[index, 'tau_fwhm_final'] = new_beam.tau_fwhm

            self.df.at[index, 'type'] = elem.type
            self.df.at[index, 'w_0'] = old_beam.w_0
            self.df.at[index, 'z_from_w_0_start'] = old_beam.z_from_w_0
            self.df.at[index, 'z_from_w_0_final'] = new_beam.z_from_w_0

            self.df.at[index, 'power_avg_final'] = new_beam.power_avg
            self.df.at[index, 'width'] = elem.width
            self.df.at[index, 'max_intensity'] = new_beam.I_max
        logger.info('Finished row calculations')
        logger.info(f'Columns {self.df.columns}')

    def make_flat_df(self):
        step = 0.005
        logger.info('Creating flat dataframe.')
        z_lst = np.array(self.df.z)
        dz_lst = np.array(self.df.width)
        element_lst = self.df.element
        beam_start_lst = self.df.init_beam_profile
        index_lst = self.df.index

        # FIRST THING
        z_flat = []
        w_z_flat = []
        z_from_w_0_flat = []
        tau_fwhm = []
        max_intensity = []


        for index, dz, z, element in zip(index_lst, dz_lst, z_lst, element_lst):
            series = self.df.iloc[index]
            logger.debug(f'{series=}')
            w_0 = series['w_0']
            z_from_w_0_start = series['z_from_w_0_start']

            lambda_0 = beam_start_lst[index].wavelength_center
            if element.width > 0:
                z_calcs = np.arange(0, dz, step)
                if np.max(np.shape(z_calcs)) < 1:
                    z_calcs = [0]
                if z_calcs[-1] > element.width:
                    z_calcs[-1]=element.width

                w_z_calc = np.zeros(np.shape(z_calcs))
                for i, z_rel in enumerate(z_calcs):
                    w_z_calc[i] = gauss_envelope(w_0, z_from_w_0_start+z_rel, lambda_0)
                logger.info(f'{w_z_calc[i]=:.3e}, {z_rel=:.3e}, {z_from_w_0_start=:.3e}, {z + z_calcs[i] =}, {str(element).split('(')[0]}')

                # SECOND THING
                w_z_flat.extend(w_z_calc)
                z_flat.extend(z + z_calcs)
                tau_fwhm.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'tau_fwhm_init'])
                max_intensity.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'max_intensity'])
            else:

                # THIRD THING
                z_flat.append(z)
                w_z_flat.append(self.df.at[index, 'w_z_start'])
                tau_fwhm.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'tau_fwhm_init'])
                max_intensity.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'max_intensity'])

        plt.plot(z_flat, w_z_flat, '.')
        plt.savefig('test.png')
                            # FOURTH THING
        flat_df = pd.DataFrame({'z': z_flat, 'w_z': w_z_flat, 'tau_fwhm': tau_fwhm, 'max_intensity': max_intensity})
        flat_df.to_csv('test_df.csv')
        with open('element_set.json', 'w') as f:
            json.dump(str(self.element_set), f)
                

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



def main():

    from my_logging import configure_logging
    configure_logging()
    logger.info('Running layout.py as __main__')
    sim_setup()
if __name__ == '__main__':
    main()
