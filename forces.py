import numpy as np

class Forces:
    def __init__(self, dam):
        """
        Initialize the Forces class with a dam object.
        The dam object provides geometry and other essential parameters for force calculation.
        """
        self.dam = dam  # retrieve dam geometry and parameters from the Dam object
        self.status = {
            'partial_empty': {},
            'reservoir_empty': {},
            'reservoir_full': {},
            'sliding_check': None
        }  # Status object for tracking forces, lever arms, and moments, and sliding coeff.

        # Precompute section weights and forces
        self.forces, self.lever_arms = self._calculate_forces_and_levers()

    def _calculate_section_weights(self) -> dict:
        """
        Calculate the self-weights of dam sections W1 (upright), W2 (downstream slope), W3 (upstream slope).
        These forces act vertically due to gravity.
        """
        # Dam geometry parameters
        geom = self.dam.geometry

        # W1: Weight of the upright section (top width)
        W1 = self.dam.gamma_c * geom['top_width'] * (geom['effective_height'] + self.dam.freeboard)

        # W2: Weight of the downstream slope section
        W2_base = geom['downstream_base_width'] - geom['top_width']
        W2_height = geom['effective_height'] - geom['crest_elevation']
        W2 = 0.5 * W2_base * W2_height * self.dam.gamma_c

        # W3: Weight of the upstream slope section
        W3 = 0.5 * geom['upstream_base_width'] * geom['upstream_slope_height'] * self.dam.gamma_c

        return {
            'W1': W1,
            'W2': W2,
            'W3': W3
        }

    def _calculate_wave_pressure(self) -> float:
        """
        Calculate the wave pressure force acting horizontally on the dam.
        """
        return 2 * self.dam.gamma_w * np.square(self.dam.hw)

    def _calculate_fv(self) -> float:
        """
        Calculate the vertical force due to the water column.
        """
        return 0.75 * self.dam.gamma_w * self.dam.geometry['effective_height'] * self.dam.geometry['upstream_base_width']

    def _calculate_uplift_force(self) -> float:
        """
        Calculate the uplift force, which acts vertically upwards and opposes the weight of the dam.
        """
        return -self.dam.uplift_factor * self.dam.geometry['dam_base_width'] * (self.dam.geometry['effective_height'] / 2) * self.dam.gamma_w

    def _calculate_water_pressure(self) -> float:
        """
        Calculate the water pressure acting horizontally on the dam.
        """
        return 0.5 * self.dam.gamma_w * np.square(self.dam.geometry['effective_height'])

    def _calculate_lever_arms(self) -> dict:
        """
        Calculate the lever arms for each force, which determine the distance from the point of action to the reference point (usually the base of the dam).
        """
        geom = self.dam.geometry

        # Lever arms for each force
        l1 = geom['crest_elevation'] + (geom['top_width'] / 2)  # W1
        l2 = geom['downstream_base_width'] - geom['top_width'] # W2
        l3 = geom['upstream_slope_length'] + ((2/3) * geom['upstream_base_width'])  # W3
        lv = geom['upstream_slope_length'] + (geom['upstream_base_width'] / 2)  # Water column (Fv)
        lu = geom['upstream_slope_length'] + (geom['dam_base_width'] / 3)  # Uplift force (Fu)
        lh = geom['effective_height'] / 3  # Water pressure (Fh)
        lwa = geom['effective_height'] + self.dam.point_of_application  # Wave action (Fwv)

        return {
            'W1': l1,
            'W2': l2,
            'W3': l3,
            'Fv': lv,
            'Fu': lu,
            'Fh': lh,
            'Fwv': lwa
        }

    def _calculate_forces_and_levers(self) -> tuple:
        """
        Calculate all forces acting on the dam and their respective lever arms.
        Return forces and lever arms as dictionaries.
        """
        # Calculate section weights (W1, W2, W3)
        section_weights = self._calculate_section_weights()

        # Other forces
        Fwv = self._calculate_wave_pressure()  # Wave pressure (horizontal)
        Fv = self._calculate_fv()  # Water column (vertical)
        Fu = self._calculate_uplift_force()  # Uplift force (vertical)
        Fh = self._calculate_water_pressure()  # Water pressure (horizontal)

        # Collect all forces in a dictionary
        forces = {
            'W1': section_weights['W1'],
            'W2': section_weights['W2'],
            'W3': section_weights['W3'],
            'Fv': Fv,
            'Fu': Fu,
            'Fh': Fh,
            'Fwv': Fwv
        }

        # Calculate lever arms for all forces
        lever_arms = self._calculate_lever_arms()

        return forces, lever_arms

    def calculate_moments(self) -> dict:
        """
        Calculate moments for each force based on the lever arms.
        Return a dictionary of moments.
        """
        moments = {key: self.forces[key] * self.lever_arms[key] for key in self.forces}
        return moments

    def calculate_sums(self):
        """
        Calculate the total horizontal and vertical forces and moments for different dam conditions:
        - Partial empty
        - Reservoir empty
        - Reservoir full

        This method will compute the correct force sums, lever arm weighted averages, and moments.
        """
        # Extract calculated forces and lever arms
        W1, W2, W3 = self.forces['W1'], self.forces['W2'], self.forces['W3']
        Fv = self.forces['Fv']
        Fu = self.forces['Fu']
        Fh = self.forces['Fh']
        Fwa = self.forces['Fwv']

        # PARTIAL EMPTY (No W3 or water-related forces)
        partial_empty_vertical_sum = W1 + W2
        partial_empty_moment_sum = (W1 * self.lever_arms['W1']) + (W2 * self.lever_arms['W2'])
        partial_empty_lever_arm_avg = partial_empty_moment_sum / partial_empty_vertical_sum

        # RESERVOIR EMPTY
        reservoir_empty_vertical_sum = W1 + W2 + W3
        reservoir_empty_moment_sum = (W1 * self.lever_arms['W1']) + (W2 * self.lever_arms['W2']) + (W3 * self.lever_arms['W3'])
        reservoir_empty_lever_arm_avg = reservoir_empty_moment_sum / reservoir_empty_vertical_sum

        # RESERVOIR FULL
        reservoir_full_vertical_sum = W1 + W2 + W3 + Fv + Fu
        reservoir_full_horizontal_sum = Fh + Fwa
        reservoir_full_moment_sum = (
            (W1 * self.lever_arms['W1']) +
            (W2 * self.lever_arms['W2']) +
            (W3 * self.lever_arms['W3']) +
            (Fv * self.lever_arms['Fv']) +
            (Fu * self.lever_arms['Fu']) +
            (Fh * self.lever_arms['Fh']) +
            (Fwa * self.lever_arms['Fwv'])
        )
        reservoir_full_lever_arm_avg = reservoir_full_moment_sum / (reservoir_full_vertical_sum + reservoir_full_horizontal_sum)

        # Store the sums in the status object for sliding and stress checks
        self.status['partial_empty'] = {
            'vertical_sum': partial_empty_vertical_sum,
            'moment_sum': partial_empty_moment_sum,
            'lever_arm_avg': partial_empty_lever_arm_avg
        }
        
        self.status['reservoir_empty'] = {
            'vertical_sum': reservoir_empty_vertical_sum,
            'moment_sum': reservoir_empty_moment_sum,
            'lever_arm_avg': reservoir_empty_lever_arm_avg
        }

        self.status['reservoir_full'] = {
            'vertical_sum': reservoir_full_vertical_sum,
            'horizontal_sum': abs(reservoir_full_horizontal_sum),
            'moment_sum': reservoir_full_moment_sum,
            'lever_arm_avg': reservoir_full_lever_arm_avg
        }

    def check_sliding(self):
        """
        Check sliding stability using the ratio of horizontal to vertical forces.
        """
        reservoir_full_status = self.status['reservoir_full']
        sliding_ratio = reservoir_full_status['horizontal_sum'] / reservoir_full_status['vertical_sum']

        check = sliding_ratio < self.dam.friction_coefficient  # True if safe against sliding, False if not

        sliding_report_map = {True: f'{sliding_ratio} < {self.dam.friction_coefficient}, Friction alone is sufficient!',
                              False: f'FAILURE: Friction alone is insufficient ({sliding_ratio} > {self.dam.friction_coefficient})'}

        self.status['sliding_check'] = sliding_report_map[check]
