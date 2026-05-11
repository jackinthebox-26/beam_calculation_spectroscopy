import numpy as np
from dataclasses import dataclass
import json

from loguru import logger

    

@dataclass
class optical_element:
    """This is the container class for all optical elements and loads their properties."""
    configfile: str 
    def __post_init__(self):
        self.json_config = self.load_config()
        self.type = self.json_config['type']
        self.width = self.json_config['width']
        self.transmission = self.json_config.get('transmission', 1)
        self.index = self.json_config.get('index', 1)
        self.aperture = self.json_config.get('aperture', 1)
        if 'GDD' in self.json_config:
            self.GDD = self.json_config['GDD']
        elif 'GVD' in self.json_config:
            self.GDD = self.json_config['GVD'] * self.width
        else:
            self.GDD = 0
        
    def load_config(self):
        """This method loads the config data."""
        file = self.configfile
        with open(file, 'r') as f:
            config = json.load(f)
        return config
@dataclass
class Space:
    width: float
    index: float = 1
    GDD: float = 0
    def __post_init__(self):
        self.type = 'Space'
        
    def get_ABCD(self):
        A = 1
        B = self.width / self.index
        C = 0
        D = 1
        return (A, B, C, D)

    def get_jones_matrix(self):
        A = 1
        B = 0
        C = B
        D = A
        return (A, B, C, D)

class Lens(optical_element):
    """This class contains the equations and properties of lenses."""
    def __post_init__(self):
        super().__post_init__()
        self.focal_length = self.json_config['focal_length']
        self.width = self.json_config.get('width', 2e-3)
        self.name = self.json_config.get('name', f'Lens with f={self.focal_length}')
        

    def __str__(self):
        return f'Lens(name={self.name}, f={self.focal_length})'

    def get_ABCD(self):
        focal_length = self.focal_length
        A = 1
        B = 0 
        C = -1 / focal_length
        D = 1
        return (A, B, C, D)
    def get_jones_matrix(self):
        A = 1
        B = 0
        C = B
        D = A
        return (A, B, C, D)
    


class HWP(optical_element):
    """This class contains the equations and properties of HWP."""
    def __post_init__(self):
        super().__post_init__()
        self.angle = self.json_config['angle']

    def __str__(self):
        return(f'HWP(angle={self.angle:.3f})')

    def get_ABCD(self):
        A = 1
        B = self.width
        C = 0
        D = A
        return (A, B, C, D)

    def get_jones_matrix(self):
        angle = self.angle
        A = np.cos(angle) ** 2 - np.sin(angle) ** 2 
        B = 2 * np.cos(angle) * np.sin(angle)
        C = B
        D = np.sin(angle) ** 2  - np.cos(angle) ** 2
        return (A, B, C, D)

class QWP(optical_element):
    """This class contains the equations and properties of QWP."""
    def __post_init__(self):
        super().__post_init__()
        self.angle = self.json_config['angle']
    def __str__(self):
        return f'QWP(angle={self.angle:.3f})'
    def get_ABCD(self):
        A = 1
        B = self.width
        C = 0
        D = A
        return (A, B, C, D)

    def get_jones_matrix(self):
        angle = self.angle
        A = np.cos(angle) ** 2 + (np.sin(angle) ** 2) * 1j
        B = (1 - 1j) * np.sin(angle) * np.cos(angle)
        C = (1 - 1j) * np.sin(angle) * np.cos(angle)
        D = np.sin(angle) ** 2 + (np.cos(angle) ** 2) * 1j
        return (A, B, C, D)

class PBC(optical_element):
    """This class contains the equations and properties of PBC."""
    def __post_init__(self):
        super().__post_init__()
        self.arm = self.json_config['arm']

    def __str__(self):
        return f'PBC(arm={self.arm})'

    def get_ABCD(self):
        A = 1
        B = self.width
        C = 0
        D = A
        return (A, B, C, D)
    def get_jones_matrix(self):
        if self.arm == 'T':
            A = 1
            B = 0
            C = B
            D = 0
        else:
            A=0
            B=0
            C=B
            D=1
        return (A, B, C, D)

def main():
    logger.info("Begin testing optical_element_object file.")
    folder = '../config/'
    coll_lens = Lens(folder + 'config_coll_lens.json')
    coll_lens = Lens(folder + 'config_lens_thorlabs_LA4380_UV.json')
    logger.info(coll_lens)
if __name__ == "__main__":
    main()
