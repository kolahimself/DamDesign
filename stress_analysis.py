import numpy as np 


class StressAnalysis:
    def __init__(self, forces):
        """
        Initialize the StressAnalysis class with the forces object.
        The forces object provides the force, lever arm, and moment data.
        """
        self.forces = forces  # The Forces object that contains sums and status information
        self.safety_limit = 4000  # Stress safety bearing capacity of rock/soil in kPa

    def _calculate_eccentricity(self, condition: str, dam_width: float) -> float:
        """
        Calculate the eccentricity 'e' for the given condition (reservoir_empty or reservoir_full).
        Eccentricity is defined as the distance between the resultant force's line of action and the center of the base.
        e = ΣM / ΣV and less than or equal to B / 6
        """
        vertical_sum = self.forces.status[condition]['vertical_sum']
        moment_sum = self.forces.status[condition]['moment_sum']
        
        # Avoid division by zero
        if vertical_sum == 0:
            return 0
        
        # Determine eccentricity, applying middle thirds limit
        return min(moment_sum / vertical_sum, dam_width / 6)

    def _calculate_stresses(self, condition: str) -> dict:
        """
        Calculate the vertical pressures at the toe (p_v') and heel (p_v'') of the dam for the given condition.
        Use the formula:
        p_v' , p_v'' = ΣW / B (1 ± 6e / B)
        Where B is the base width, ΣW is the vertical force, and e is the eccentricity.
        """
        # Retrieve vertical sum and base width
        vertical_sum = self.forces.status[condition]['vertical_sum']
        base_width = self.forces.dam.geometry['dam_base_width']
        
        # Calculate eccentricity 'e'
        eccentricity = self._calculate_eccentricity(condition, base_width)

        # Calculate stresses at the heel (p_v') and toe (p_v'') of the dam
        p_v_prime = (vertical_sum / base_width) * (1 + (6 * eccentricity / base_width))
        p_v_prime_prime = (vertical_sum / base_width) * (1 - (6 * eccentricity / base_width))

        # Calculate the effective vertical stress at a specific point in the dam
        phi = 90 - self.forces.dam.geometry['upstream_slope_angle']
        p_i_prime = p_v_prime * (1 + np.square(np.tan(np.radians(phi))))

        return {
            'heel_stress': p_v_prime_prime,  # Vertical Stress at the heel (downstream side)
            'effective_vertical_stress': p_i_prime  # Effective vertical stress in the dam 
        }

    def run_checks(self):
        """
        Run stress checks for both reservoir empty and reservoir full conditions.
        Compare calculated stresses with the safety limit and report whether the dam is safe.
        """
        conditions = ['reservoir_empty', 'reservoir_full']
        results = {}

        for condition in conditions:
            stresses = self._calculate_stresses(condition)
            
            heel_stress = stresses['heel_stress']
            eff_stress = stresses['effective_vertical_stress']

            # Check if the stresses are within safe limits
            if heel_stress < self.safety_limit and eff_stress < self.safety_limit:
                results[condition] = f"Safe: Heel Stress = {heel_stress:.2f} kPa, Effective Vertical Stress = {eff_stress:.2f} kPa"
            else:
                results[condition] = f"Unsafe: Heel Stress = {heel_stress:.2f} kPa, Effective Vertical Stress = {eff_stress:.2f} kPa"

        return results

    def __repr__(self):
        return f"<StressAnalysis(safety_limit={self.safety_limit})>"
