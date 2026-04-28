import numpy as np
from dataclasses import dataclass

@dataclass
class gaussian_beam:
    wavelength_center: float 
    wavelength_fwhm: float
    power_avg: float
    w_0: float
    index: float = 1
    z_from_w_0: float = 0
    gdd_initial: float = 0
    jones_matrix: float = 0
    record: float = ''

    def __post_init__(self):
        self.z_R = self.rayleigh_range()
        self.w_z = self.spot_size()
        self.R_z = self.radius_of_curvature()
        self.q_z = self.beam_param()
        self.I_max = self.max_intensity()

    def __str__(self):
        width = 50
        def outline(width=width):
            return '=' * width 
        def inline(width=width):
            return '-' * width 
        def formatting(string, width=width):
            return f'|{string:{width}}|\n'
        def add_line(self, name, width=width, unit=None, scale=1, form='.2f'):
            if unit is None: unit= ''
            return formatting(f'{name}: {getattr(self, name)*scale:{form}} {unit}', width)

        midline = formatting(inline())

        string = formatting(outline())
        string += add_line(self, 'wavelength_center', unit='nm', scale = 1e9)
        string += add_line(self, 'wavelength_fwhm', unit='nm', scale = 1e9)
        string += midline
        string += add_line(self, 'power_avg', unit='W')
        string += add_line(self, 'w_0', unit='mm', scale=1e3)
        string += add_line(self, 'z_R', unit='m')
        string += add_line(self, 'index')
        string += midline
        string += add_line(self, 'z_from_w_0', unit='m')
        string += add_line(self, 'w_z', unit='mm', scale=1e3)
        string += add_line(self, 'R_z', unit='m')
        string += add_line(self, 'I_max', unit='W/m2')
        string += midline
        string += add_line(self, 'q_z')
        string += midline
        string += str(self.record)
        string += formatting(outline())
        return string

    def rayleigh_range(self):
        return np.pi * self.w_0 ** 2 * self.index / self.wavelength_center

    def spot_size(self):
        return self.w_0 * np.sqrt(1+ (self.z_from_w_0/self.z_R)**2)

    def radius_of_curvature(self):
        try:
            return self.z_from_w_0 * (1 + (self.z_R / self.z_from_w_0) ** 2)
        except ZeroDivisionError:
            return 0
    def beam_param(self):
        return self.z_from_w_0 + self.z_R * 1j
    def max_intensity(self):
        return 2 * self.power_avg / (np.pi * self.w_z)


    def pass_distance(self, d):
        self.record = self.record + f'Pass a distance {d} m\n'
        return self

    def pass_lens(self, f):
        self.record = self.record + f'Pass through a lens with focal length {f*1e3} mm\n'
        return self
        
    def pass_HWP(self, angle):
        self.record = self.record + f'Pass through a HWP at angle {angle} deg\n'
        return self
        
    def pass_QWP(self, angle):
        self.record = self.record + f'Pass through a QWP at angle {angle} deg\n'
        return self
        
    def pass_PBC(self, arm):
        self.record = self.record + f'Pass through a PBC through the {arm} arm.\n'
        return self

def sim_setup():
    gauss = gaussian_beam(256e-9, 10e-9, 1, 1e-3)
    gauss = gauss.pass_distance(1)
    gauss = gauss.pass_lens(1)
    gauss = gauss.pass_HWP(1)
    gauss = gauss.pass_QWP(1)
    gauss = gauss.pass_PBC('T')
    print(gauss)

def main():
    sim_setup()
if __name__ == '__main__':
    main()
