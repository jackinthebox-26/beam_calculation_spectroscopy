from dataclasses import dataclass
import numpy as np
import scipy as sp
from loguru import logger
@dataclass
class gaussian_beam:
    """
    This class contains all information about the beam at a particular location along the optical path. This class calculates relevant properties as it interacts with free space and optical elements.
    """
    w_0: float
    power_avg: float = 1
    wavelength_fwhm: float = 10e-9
    wavelength_center: float = 256e-9 
    z_from_w_0: float = 0
    hpol: float = 0  # Input horizontal polarization
    vpol: float = 1  # 
    f_rep: float = 75e6
    tau_fwhm: float = 0

    def __post_init__(self):
        self.z_R = self.rayleigh_range()
        self.w_z = self.spot_size()
        self.R_z = self.radius_of_curvature()
        self.q_z = self.beam_param()
        self.I_max = self.max_intensity()
        self.vec = np.array([[self.hpol],[self.vpol]])
        self.gouy = self.gouy_phase()
        self.tau_lim = self.limited_pulse_length()
        if self.tau_fwhm == 0: self.tau_fwhm = self.tau_lim
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
        string += add_line(self, 'tau_lim', unit='fs', scale = 1e15)
        string += midline
        string += add_line(self, 'power_avg', unit='W')
        string += add_line(self, 'w_0', unit='mm', scale=1e3)
        string += add_line(self, 'z_R', unit='m')
        string += midline
        string += add_line(self, 'z_from_w_0', unit='m')
        string += add_line(self, 'w_z', unit='mm', scale=1e3)
        string += add_line(self, 'R_z', unit='m')
        string += add_line(self, 'I_max', unit='W/m2')
        string += add_line(self, 'gouy')
        string += midline
        string += add_line(self, 'q_z')
        string += midline
        string += add_line(self, 'hpol')
        string += add_line(self, 'vpol')
        string += formatting(outline())
        return string

    def __repr__(self):
        return str(self.reproduce_dict())

    def rayleigh_range(self):
        """ Calculate the rayleigh range from the wavelength and beam waist."""
        z_R = np.pi * self.w_0 ** 2  / self.wavelength_center
        logger.debug(f'Calculate {z_R=}')
        return z_R

    def spot_size(self):
        """ Calculate the beam spot size using the beam waist, rayleigh range, and location."""
        w_z = self.w_0 * np.sqrt(1+ (self.z_from_w_0/self.z_R)**2)
        logger.debug(f'Calculate {w_z=}')
        return w_z

    def radius_of_curvature(self):
        """Calculate the radius of curvature using the rayleigh range and location."""
        if self.z_from_w_0 != 0:
            R = self.z_from_w_0 * (1 + (self.z_R / self.z_from_w_0) ** 2)
        else:
            logger.warning('Divide by zero issue resolved by setting R=np.inf')
            R = np.inf
        logger.debug(f'Calculate {R=}')
        return R


    def beam_param(self):
        """Calculate the beam parameter using the rayleigh range and location."""
        q = self.z_from_w_0 + self.z_R * 1j
        logger.debug(f'Calculate {q=}')
        return q
    def pulse_energy(self):
        """Calculate the energy in a single pulse."""
        E_pulse = self.power_avg / self.f_rep
        logger.debug(f'Calculate {E_pulse=}')

    def max_intensity(self):
        """Calculate the maximum intensity of the gaussian beam."""
        I = 2 * self.power_avg / (np.pi * self.w_z ** 2)
        I = I / self.tau_fwhm
        logger.debug(f'Calculate {I=}')
        return I

    def gouy_phase(self):
        """Calculate the gouy phase of the beam."""
        gouy = np.arctan(self.z_from_w_0 / self.z_R)
        logger.debug(f'Calculate {gouy=}')
        return gouy

    def bandwidth_hz(self):
        """Calculate the bandwidth of the pulse in Hz."""
        c = sp.constants.c
        lambda_0 = self.wavelength_center
        lambda_fwhm = self.wavelength_fwhm
        nu_start = c / (lambda_0 + lambda_fwhm/2)
        nu_stop = c / (lambda_0 - lambda_fwhm/2)
        frequency_fwhm = abs(nu_stop - nu_start)
        logger.debug(f'Calculate {frequency_fwhm=}')
        return frequency_fwhm

    def limited_pulse_length(self):
        """Calculate the shortest possible pulse for the spectrum (bandwidth-limited)."""
        frequency_fwhm = self.bandwidth_hz()
        tau_fwhm = 0.441 / frequency_fwhm
        logger.debug(f'Calculate {tau_fwhm=}')
        return tau_fwhm




    def reproduce_dict(self):
        """This creates a dictionary which can re-create the current instance."""
        args = {self.w_0, }
        kwargs = {}
        kwargs['wavelength_center'] = self.wavelength_center
        kwargs['wavelength_fwhm'] = self.wavelength_fwhm
        kwargs['power_avg'] = self.power_avg
        kwargs['z_from_w_0'] = self.z_from_w_0
        kwargs['hpol'] = self.hpol
        kwargs['vpol'] = self.vpol
        kwargs['tau_fwhm'] = self.tau_fwhm

        return args, kwargs



    def apply_ABCD(self, A, B, C, D):
        """Apply an ABCD matrix to the current beam and determine the output q."""
        q = self.q_z
        q_out = (A * q + B) / (C * q + D)
        logger.debug('Calculating {q_out=}')
        return q_out

    def pass_ABCD(self, element):
        """Create a new spot from an ABCD matrix."""
        A, B, C, D = element.get_ABCD()
        logger.debug('Applying ABCD matrix.')
        q_out = self.apply_ABCD(A, B, C, D)
        args, kwargs = self.reproduce_dict()
        kwargs['z_from_w_0'] += element.width
        
        new_spot = self.from_q(q_out, *args, **kwargs)
        return new_spot

    def pass_element(self, element):
        """Create a new spot from an optical element."""
        logger.info(f'    Passing element of type {element.type}')

        new_spot = self.pass_ABCD(element)
        new_spot = new_spot.pass_pol(*element.get_jones_matrix())
        new_spot = new_spot.pass_GDD(element.GDD)
        return new_spot


    def jones_calc(self, A, B, C, D):
        """Calculate a new jones vector from a jones matrix."""
        matrix = np.array([[A, B], [C, D]])
        new_vec = np.matmul(matrix, self.vec)

        return new_vec

    def pass_pol(self, A, B, C, D):
        """Create a new spot from a Jones matrix."""
        new_vec = self.jones_calc(A, B, C, D)
        old_dict = self.reproduce_dict()
        old_dict['kwargs'].pop('hpol')
        old_dict['kwargs'].pop('vpol')
        if (old_norm := find_norm(new_vec)) < 0.999:  # This decreases the power due to polarization filtering.
            P_new = self.power_avg * old_norm
            old_dict['power_avg'] = P_new
            new_vec /= np.sqrt(old_norm)
        new_spot = self.from_pol(new_vec, **old_dict)
        return new_spot
                          



    @classmethod
    def from_q(cls, q, wavelength_center, wavelength_fwhm, power_avg, kwargs=None):
        """Return an instance with the specified q."""
        if kwargs is None: kwargs = {}
        z_from_w_0 = q.real
        z_R = q.imag

        w_0 = np.sqrt(z_R * wavelength_center/ np.pi)

        return cls(wavelength_center, wavelength_fwhm, power_avg, w_0, z_from_w_0=z_from_w_0, **kwargs) 


    @classmethod
    def from_pol(cls,new_vec, wavelength_center, wavelength_fwhm, power_avg, w_0, kwargs=None):
        """Return an instance with the specified jones vector."""
        if kwargs is None: kwargs = {}
        hpol = new_vec[0, 0]
        vpol = new_vec[1, 0]
        return cls(wavelength_center, wavelength_fwhm, power_avg, w_0, hpol=hpol, vpol=vpol, **kwargs)

def find_norm(vec):
    return np.abs(vec[0, 0]) ** 2 + np.abs(vec[1, 0]) ** 2
def main():
    from my_logging import configure_logging
    configure_logging()
    logger.info('Running gaussian_beam_slice.py as __main__.')
    print(gaussian_beam(256e-9, 10e-9, 1, 0.1e-3))


if __name__ == "__main__":
    main()
