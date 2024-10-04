from dam import Dam
from forces import Forces
from stress_analysis import StressAnalysis


def load_design_params(file_path: str) -> dict:
    """
    Load design parameters and utility factors from a YAML file.
    """
    with open(file_path, 'r') as file:
        params = yaml.safe_load(file)
    return params


def report_dam_design(dam: Dam, forces_status: dict, stress_results: dict):
    """
    Report the results of dam geometry, forces, and stress analysis.
    """
    # Print dam geometry details
    print("Dam Geometry:")
    for key, value in dam.get_dam_properties()['geometry'].items():
        print(f"  {key}: {value:.2f}")

    print("\nWave Characteristics:")
    print(f"  Wave Height: {dam.hw:.2f} m")
    print(f"  Rise of Wave: {dam.rise_of_wave:.2f} m")
    print(f"  Freeboard: {dam.freeboard:.2f} m")
    print(f"  Wave Force Application Point: {dam.point_of_application:.2f} m")

    # Forces and moments
    print("\nForce Calculations:")
    print(f"  Vertical Forces (Reservoir Full): {forces_status['reservoir_full']['vertical_sum']:.2f} kN")
    print(f"  Horizontal Forces (Reservoir Full): {forces_status['reservoir_full']['horizontal_sum']:.2f} kN")

    # Sliding Check
    print("\nSliding Check:")
    print(forces_status['sliding_check'])

    # Stress analysis
    print("\nStress Analysis Results:")
    for condition, result in stress_results.items():
        print(f"  {condition.capitalize()}: {result}")

def prompt_design_params():
    print("Please enter the following design parameters:")
    
    # Collecting design parameters from the user
    h_max = float(input("Max depth of headwater (m): ") or 45)
    he = float(input("Distance from spillway crest to MWL (m): ") or 3)
    top_width = float(input("Width of dam crest (m) : ") or 7.5)
    gamma_c = float(input("Unit weight of concrete (kN/m³): ") or 22)
    gamma_w = float(input("Unit weight of water (kN/m³): ") or 10)
    friction_coefficient = float(input("Friction coefficient for sliding checks [default: 0.75]: ") or 0.75)
    fetch_length = float(input("Fetch length (km): ") or 5)
    uplift_factor = float(input("Uplift factor: ") or 0.5)
    wind_velocity = float(input("Wind velocity (km/h): ") or 128)

    # Collecting utility factors from the user
    hw_amplification_factor = float(input("Wave height amplification factor [default: 1.33]: ") or 1.33)
    freeboard_allowance = float(input("Safety freeboard allowance (m) [default: 0.14]: ") or 0.14)

    # Return the collected parameters as a dictionary
    return {
        'design_params': {
            'h_max': h_max,
            'he': he,
            'top_width': top_width,
            'gamma_c': gamma_c,
            'gamma_w': gamma_w,
            'friction_coefficient': friction_coefficient,
            'fetch_length': fetch_length,
            'uplift_factor': uplift_factor,
            'wind_velocity': wind_velocity,
        },
        'utils': {
            'hw_amplification_factor': hw_amplification_factor,
            'freeboard_allowance': freeboard_allowance,
        }
    }

def main():
    # Step 1: Prompt the user for design parameters
    design_params = prompt_design_params()

    # Step 2: Extract the dam design parameters and utility factors from the collected data
    dam_params = design_params['design_params']
    utils = design_params['utils']

    # Step 3: Initialize the Dam object
    dam = Dam(dam_params, utils)

    # Step 4: Initialize the Forces object with the Dam object
    forces = Forces(dam)

    # Step 5: Precompute force sums for partial, empty and full conditions
    forces.calculate_sums()  

    # Step 6: Check against sliding
    forces.check_sliding()

    # Step 6: Initialize the StressAnalysis object with the Forces object
    stress_analysis = StressAnalysis(forces)

    # Step 7: Run stress checks
    stress_results = stress_analysis.run_checks()

    # Step 8: Report the results of the dam design and calculations
    report_dam_design(dam, forces.status, stress_results)

if __name__ == "__main__":
    main()