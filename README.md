# StirTankCFD

StirTankCFD is a Python-based CFD tool especially for stirred tanks with impellers.

The project automates:
- Geometry generation
- Meshing
- Solver setup
- MRF configuration
- Simulation execution
- Post-processing
- Visualization

through a single GUI interface.

---

# Installation

I am using Ubuntu since a very long time and do not have much idea about the installation of this environment on Windows.

## Ubuntu Installation

```bash
git clone https://github.com/jatinguliani/StirTankCFD.git

cd StirTankCFD

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

# Dependencies

- OpenFOAM v2406
- Python 3.x
- CadQuery
- PyQt6
- PyVista
- Matplotlib
- NumPy

---

# How the Code Works

The project is divided into a few main parts.

## templates/

This folder contains the base OpenFOAM stirred tank case. Every time a new simulation is started, the software copies this case and automatically updates the dictionaries based on the inputs from the GUI. This is similar to how CFD engineers usually reuse validated base cases in real workflows.

Technologies Used:
- OpenFOAM

---

## tank_builder.py and impeller_builder.py

These scripts generate the tank and impeller geometry automatically using CadQuery. The dimensions entered in the GUI are converted into STL geometry files which are later used for meshing.

Technologies Used:
- Python
- CadQuery

---

## case_builder.py

case_builder is the main script that first launches the GUI, which takes the values from the user and passes them to the impeller and tank generation scripts which produce the STL files.

After that, the case_builder checks and creates the necessary blockMesh dynamically based on the user-provided tank size and also changes the mesh cells accordingly.

Later, blockMesh, snappyHexMesh and the solver are run sequentially followed by extracting the CSV files for the U and P values that can be used for further data analysis.

Technologies Used:
- Python
- OpenFOAM
- subprocess automation

---

## post_process.py

This script handles the post-processing stage and generates:
- CSV files
- Residual plots
- Contour screenshots
- GIF animations

Post-processing can also be done better in ParaView, so that can be installed separately by the user and run inside the generated case folder for advanced visualization.

Technologies Used:
- Python
- NumPy
- Matplotlib
- PyVista
- VTK

---

## gui.py

This is the graphical interface of the project built using PyQt6. It allows the user to define all simulation parameters such as:
- Tank dimensions
- Impeller dimensions
- RPM
- Mesh density
- Fluid properties

and run the complete CFD pipeline from a single interface.

Technologies Used:
- Python
- PyQt6
