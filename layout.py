""" TODO
Complete docs
optical setup in json or other config file

Verify calculatoins while implementing test cases.

Add optical elements to plots

"""
"""
This file 
"""

# Standard library imports
import json
from dataclasses import dataclass

# Open source library imports
from loguru import logger
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Custom library imports
from gaussian_beam_slice import gaussian_beam
from optical_element_objects import Lens, QWP, HWP, PBC, Space


def gauss_envelope(w_0, z_from_w_0, wavelength_center, index = 1):
    """Returns the beam size at a particulat location. """
    z_R = np.pi * w_0 ** 2 * index / wavelength_center
    return w_0 * np.sqrt(1 + (z_from_w_0 / z_R)**2)

@dataclass
class optical_layout:
    """This class runes through a particular optical layout and creates a database for future analysis."""
    init_beam: gaussian_beam  # This is the beam at the point it enters the optical setup
    element_set: tuple  # This contains a list of optical component and the spaces between them
    step: float = 0.005
    def __post_init__(self):
        self.df = self.init_df()  # Initiate the dataframe
        self.row_calcs()  # Do the full calculation for every row
        self.make_flat_df()  # 
        
    
    def init_df(self):
        """This method initiates the dataframe from the element set and finds the dz and z. """
        logger.info('Begin intiating dataframe.')

        # Find the width of all the elements
        dz = []
        for index, element in enumerate(self.element_set):
            dz.append(element.width)

        logger.debug(f'{dz=}')

        # Find the z location of each element
        z = [0]
        for i, new_z in enumerate(dz):
            z.append(z[i] + new_z)
        z.pop()

        logger.debug(f'{z=}')
        
        df = pd.DataFrame({'z': z, 'element': self.element_set})  
        logger.info('Finished initiating dataframe.')
        return df

    def row_calcs(self):
        """Calculate all the rows."""
        logger.info('Begin row calculations')

        first_beam = self.init_beam
        self.df.at[0, 'init_beam_profile'] = first_beam
        self.df['final_pol_vec'] = None
        self.df['init_pol_vec'] = None

        # Iterate through the beam propegation path
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

    def make_flat_df(self):
        """This method makes a df that can be saved to json and re-loaded without the need for the optical elements dataclass."""

        logger.info('Creating flat dataframe.')

        step = self.step
        z_lst = np.array(self.df.z)
        dz_lst = np.array(self.df.width)
        element_lst = self.df.element
        beam_start_lst = self.df.init_beam_profile
        index_lst = self.df.index

        # Initiate the values to be calculated
        z_flat = []
        w_z_flat = []
        z_from_w_0_flat = []
        tau_fwhm = []
        max_intensity = []

        # Iterate through the elements
        for index, dz, z, element in zip(index_lst, dz_lst, z_lst, element_lst):
            series = self.df.iloc[index]
            logger.debug(f'{series=}')
            w_0 = series['w_0']
            z_from_w_0_start = series['z_from_w_0_start']

            lambda_0 = beam_start_lst[index].wavelength_center

            # Analyse across the length of the object.
            if element.width > 0:
                z_calcs = np.arange(0, dz, step)
                if np.max(np.shape(z_calcs)) < 1:
                    z_calcs = [0]
                if z_calcs[-1] > element.width:
                    z_calcs[-1]=element.width

                w_z_calc = np.zeros(np.shape(z_calcs))
                for i, z_rel in enumerate(z_calcs):
                    w_z_calc[i] = gauss_envelope(w_0, z_from_w_0_start+z_rel, lambda_0)
                logger.debug(f'{w_z_calc[i]=:.3e}, {z_rel=:.3e}, {z_from_w_0_start=:.3e}, {z + z_calcs[i] =}, {str(element).split('(')[0]}')

                w_z_flat.extend(w_z_calc)
                z_flat.extend(z + z_calcs)
                tau_fwhm.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'tau_fwhm_init'])
                max_intensity.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'max_intensity'])
            else:
                # Do this if the element is essentially width-less.
                z_flat.append(z)
                w_z_flat.append(self.df.at[index, 'w_z_start'])
                tau_fwhm.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'tau_fwhm_init'])
                max_intensity.extend(np.ones(np.shape(z_calcs)) * self.df.at[index, 'max_intensity'])

        flat_df = pd.DataFrame({'z': z_flat, 'w_z': w_z_flat, 'tau_fwhm': tau_fwhm, 'max_intensity': max_intensity})
        flat_df.to_csv('test_df.csv')
        with open('element_set.json', 'w') as f:
            json.dump(str(self.element_set), f)
                

def sim_setup():
    folder = '../config/'
    space_1 = 1.2  # Space before collimating lens
    space_2 = 0.1  # Space between coll_lens and the hwp
    space_3 = 0.02  # Space betwwn hwp and pbc
    space_4 = 0.02  # Space between the pbc and the qwp
    space_5 = 1  # Space between the qwp and the focusing lens 1
    space_6 = 0.2  # Space between the focusing lens 1 and focusing lens 2
    space_7 = 4  # Space between focusing lens 2 and focusing lens 2
    coll_lens = Lens(folder + 'config_coll_lens.json')
    qwp = QWP(folder + 'config_qwp.json')
    pbc = PBC(folder + 'config_pbc.json')
    hwp = HWP(folder + 'config_hwp.json')
    focusing_lens_1 = Lens(folder + 'config_lens_thorlabs_LA4380_UV.json')
    focusing_lens_2 = Lens(folder + 'config_lens_thorlabs_LA4380_UV.json')
    element_set = (Space(space_1), 
                   hwp,
                   Space(space_3),
                   pbc, 
                   Space(space_4),
                   qwp, 
                   Space(space_5), 
                   focusing_lens_1, 
                   Space(space_6), 
                   focusing_lens_2, 
                   Space(space_7),
                   focusing_lens_2,
                   Space(space_6),
                   focusing_lens_1,
                   Space(space_5),
                   qwp,
                   Space(space_4),
                   pbc,
                   Space(space_3),
                   hwp,
                   Space(space_1)

                   )

    gauss = gaussian_beam(1e-3, z_from_w_0=0.1)


    ol = optical_layout(gauss, element_set)



def main():

    from my_logging import configure_logging
    configure_logging()
    logger.info('Running layout.py as __main__')
    sim_setup()
if __name__ == '__main__':
    main()
