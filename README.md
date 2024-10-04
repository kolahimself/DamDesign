# DamDesign
Permit my interruption, an introduction is necessary. This is a quick project I whipped up out of an impromptu neceessity of my own making.

It is an implementation of the single-step method for the analysis and design of concrete gravity dams in `python`

# Installation
1. Install `uv`:
```bash
pip install uv
```
2. Clone this repo and navigate to the project directory
```bash
git.clone link_goes_here
cd 
```
3. Initialize the project
```bash
uv init
```
4. Install dependencies
```bash
uv sync
```
5. Run the project 🚀
```bash
uv run dam_design
```

# Usage ?
Enter your design parameters and view the design report.

# Technical Notes for `v 0.1.0`
- The design ignores silt pressure, and takes the effect of earthquake to be minimal
- The model in view is a simple concrete dam with an upright, upstream and downstream sections.
- Forces analysed are highligted below:
| Section Weights | Vertical Force due to the Water Column | Uplift (-) | Water Pressure | Wave Action |
- Checks for sliding and stress checks when the reservoir is empty or full are included.

# License
This project is licensed under the MIT License - see the LICENSE file for details

# Contact
Reach me [here!](ojameskola03@gmail.com), open to further contributions & collaborations, cheeers.