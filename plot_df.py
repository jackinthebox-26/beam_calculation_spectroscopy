from loguru import logger
import json

import matplotlib.pyplot as plt
import pandas as pd
from adjustText import adjust_text

from make_config import initiate_data
from gaussian_beam_slice import gaussian_beam
from optical_element_objects import Lens, QWP, HWP, PBC, Space
from layout import optical_layout


def plot_optical_layout(df, size_scale=100):
    logger.info('plotting optical layout')
    plot_beam_width(df)
    plot_pulse_length(df)
    plot_max_intensity(df)


def plot_beam_width(df):
    logger.info('Plotting beam width')

    fig, ax = plt.subplots()

    ax.plot(df.z, df.w_z * 1e3)
    ax.set_xlabel('Distance from start of system (m)')
    ax.set_ylabel('Spot size (mm)')
    ax.grid(True)

    ax = plot_elements(ax)

    plt.show()


def plot_pulse_length(df):
    logger.info('Plotting pulse length')

    fig, ax = plt.subplots()
    ax.plot(df.z, df.tau_fwhm)
    ax.set_yscale('log')
    ax.set_xlabel('Distance from start of system (m)')
    ax.set_ylabel('Pulse length (s)')

    ax = plot_elements(ax)

    plt.show()

def plot_max_intensity(df):
    logger.info('Plotting max intensity')

    fig, ax = plt.subplots()
    print(df)
    ax.plot(df.z, df.max_intensity)
    ax.set_yscale('log')
    ax.set_xlabel('Distance from start of system (m)')
    ax.set_ylabel('Peak Power (W/m^2)')
    ax = plot_elements(ax, y=10e23)
    plt.show()

def parse_element_list(data):
    logger.info('Begining data parsing')
    list_of_strings = data[1:-1].split('),')
    class_list = [x.split('(')[0].strip(' ') for x in list_of_strings]
    data_list = [x.split('(')[1].strip(')') for x in list_of_strings]
    data_dict_list = []
    for item in data_list:
        item_dict = {}
        temp_list = item.split(',')
        for sub_item in temp_list:
            key =  sub_item.split('=')[0].strip(' ')
            value =  sub_item.split('=')[1].strip(' ').strip("'")
            try:
                value = float(value)
            except ValueError:
                pass
            item_dict[key]=value
        data_dict_list.append(item_dict)
    output_list = []
    for data_class, data in zip(class_list, data_dict_list):
        if data_class == 'Space':
            output_list.append(Space(**data))
        elif data_class == 'Lens':
            output_list.append(Lens(**data))
        elif data_class == 'HWP':
            output_list.append(HWP(**data))
        elif data_class == 'QWP':
            output_list.append(QWP(**data))
        elif data_class == 'PBC':
            output_list.append(PBC(**data))
        else:
            logger.warning(f'TODO: {data_class}')
    return output_list

def get_elements_list():
    logger.info('Fetching elements list')
    with open('element_set.json', 'r') as f:
        data = json.load(f)
    final_data = parse_element_list(data)
    return final_data

def get_z_from_elements(elements):
    logger.info('Generating the z list')
    dz_list = []
    for element in elements:
        dz_list.append(element.width)
    z_list = [0]
    for dz in dz_list:
        z_list.append(z_list[-1] + dz)
    return z_list

def label_elements(z_list, elements_list, ax, y=1):
    logger.info('Labeling elements')
    labels = [ax.text(z, y, element.type, rotation=45) for z, element in zip(z_list, elements_list)]
    adjust_text(labels, arrowprops=dict(lw=0), only_move={'text':'x'})  # This ensures that the text isn't overlapping
    return ax


def plot_elements(ax = None, y=1):
    logger.info('Plotting elements')
    element_list = get_elements_list()
    z_full = get_z_from_elements(element_list)

    filtered_z_list = [z for element, z in zip(element_list, z_full) if element.type != 'Space']
    filtered_element_list = [element for element in element_list if element.type != 'Space']

    if ax is None: fig, ax = plt.subplots()

    ax.vlines(filtered_z_list, 0,y, color='k')
    ax = label_elements(filtered_z_list, filtered_element_list, ax, y=y)

    return ax

    return ax
def sim_setup():
    df = pd.read_csv('test_df.csv')
    plot_optical_layout(df)


def main():
    from my_logging import configure_logging
    configure_logging()
    logger.info('Running plot_df.py as __main__.')
    sim_setup()


if __name__ == "__main__":
    main()

