This folder of python files performs beam propegation calculations. 
This was initially developed for xenon spectroscopy and to do the UV beam calculations.

Files
------

- `make_config.py` - This creats json files that contain the data for individual optical components
- `optical_element_objects.py` - This contains class objects (using dataclass from dataclasses) to contain the optical elements for easier use in subsequent files.
- `gaussian_beam_slice.py` - This calculates the various beam parameters as the beam propegates through the optical system.
- `layout.py` - This propegates the beam through the elements and creats a simplified dataframe that is saved to json.
- `plot_df.py` - This takes the dataframe created in layout.py and creates the plots required.
