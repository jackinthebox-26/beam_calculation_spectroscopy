from loguru import logger

import matplotlib.pyplot as plt


from make_config import initiate_data
from gaussian_beam_slice import gaussian_beam
from optical_element_objects import Lens, QWP, HWP, PBC, Space
from layout import optical_layout

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
    logger.info('Running plot_df.py as __main__.')
    sim_setup()


if __name__ == "__main__":
    main()

