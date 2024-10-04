import numpy as np


class Dam:
    def __init__(self, design_params: dict, utils: dict):
        """
        Initialize the Concrete Gravity Dam with given design parameters and utility factors
        """
        # Store design parameters
        self.h_max = design_params['h_max'] + design_params['he'] # Max depth of headwater (m)
        self.spillway_crest_to_mwl = design_params['he']  # Distance from spillway crest to MWL (m)
        self.top_width = design_params['top_width']  # Width of dam crest (m)
        self.gamma_c = design_params['gamma_c']  # Unit weight of concrete (kN/m³)
        self.gamma_w = design_params['gamma_w']  # Unit weight of water (kN/m³)
        self.friction_coefficient = design_params['friction_coefficient']  # Friction coefficient for sliding checks
        self.fetch_length = design_params['fetch_length']  # Fetch length (km)
        self.uplift_factor = design_params['uplift_factor']  # Uplift factor
        self.wind_velocity = design_params['wind_velocity']  # Wind velocity (km/h)

        # Utility factors
        self.hw_amplification_factor = utils['hw_amplification_factor']  # Factor to amplify wave height
        self.freeboard_allowance = utils['freeboard_allowance']  # Safety freeboard allowance (m)

        # Calculate and store dam geometry
        self.geometry = self._size_dam_geometry()  # Sizing the dam geometry
        
        # Precompute wave characteristics
        self.hw = self._calculate_wave_height()  # Wave height
        self.rise_of_wave = self._calculate_rise_of_wave()  # Rise of wave
        self.freeboard = self._calculate_freeboard()  # Freeboard
        self.point_of_application = self._calculate_fwv_point_of_application()  # Point of wave force application

    def _size_dam_geometry(self) -> dict:
        """
        Calculate the geometric properties of the dam.
        Returns a dictionary with key geometric parameters.
        """
        # Sizing the dam geometry based on given formulas
        h = self.h_max - self.spillway_crest_to_mwl  # Effective height (m)
        downstream_base_width = (3 * h) / 4  # Downstream base width
        upstream_base_width = h / (h + 15)  # Upstream base width
        upstream_slope_height = h / 2  # Upstream slope height
        dam_base_width = downstream_base_width + upstream_base_width  # Total base width
        crest_elevation = (4 * (h / 6)) / 3  # Crest elevation
        upstream_slope_length = crest_elevation - upstream_base_width  # Slope length
        upstream_slope_angle = np.degrees(np.arctan(upstream_slope_height / upstream_base_width))  # Slope angle in degrees

        return {
            'top_width': self.top_width,
            'effective_height': h,
            'downstream_base_width': downstream_base_width,
            'upstream_base_width': upstream_base_width,
            'upstream_slope_height': upstream_slope_height,
            'dam_base_width': dam_base_width,
            'crest_elevation': crest_elevation,
            'upstream_slope_length': upstream_slope_length,
            'upstream_slope_angle': upstream_slope_angle
        }

    def _calculate_wave_height(self) -> float:
        """
        Calculate wave height using empirical equations.
        """
        if self.fetch_length >= 32:
            hw = 0.032 * np.sqrt(self.wind_velocity * self.fetch_length)

        elif self.fetch_length < 32:
            hw = 0.763 + (0.032 * np.sqrt(self.wind_velocity * self.fetch_length)) - (0.271 * self.fetch_length**0.25)

        return hw

    def _calculate_rise_of_wave(self) -> float:
        """
        Calculate the rise of the wave near the dam structure.
        """
        return self.hw_amplification_factor * self.hw

    def _calculate_freeboard(self) -> float:
        """
        Calculate the freeboard by adding the safety allowance to the rise of wave.
        """
        return self.freeboard_allowance + self.rise_of_wave

    def _calculate_fwv_point_of_application(self) -> float:
        """
        Calculate the point of application of the wave force.
        """
        return (3 / 8) * self.hw

    def get_dam_properties(self) -> dict:
        """
        Public method to retrieve the dam's key properties (e.g., geometry, wave height).
        """
        return {
            'geometry': self.geometry,
            'wave_height': self.hw,
            'rise_of_wave': self.rise_of_wave,
            'freeboard': self.freeboard,
            'wave_force_application_point': self.point_of_application
        }

    def __repr__(self):
        return f"<Dam(height={self.h_max}, top_width={self.top_width}, base_width={self.geometry['dam_base_width']})>"
