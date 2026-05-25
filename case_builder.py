# import subprocess
# import os
# import shutil

# from tank_builder import generate_tank
# from impeller_builder import generate_impeller

# # =====================================================
# # PARAMETERS
# # =====================================================

# case_name = "case_001"

# tank_radius = 0.2
# tank_height = 0.5
# wall_thickness = 0.01
# bottom_thickness = 0.01

# shaft_radius = 0.008
# shaft_height = 0.48

# hub_radius = 0.04
# hub_height = 0.025
# hub_z = 0.2

# blade_length = 0.08
# blade_width = 0.04
# blade_thickness = 0.02

# num_blades = 4
# pitch_angle = 30

# # =====================================================
# # VALIDATION
# # =====================================================

# impeller_diameter = 2 * (hub_radius + blade_length)

# tank_diameter = 2 * tank_radius

# if impeller_diameter >= tank_diameter:
#     raise ValueError(
#         "Impeller diameter is larger than tank diameter"
#     )

# # =====================================================
# # PATHS
# # =====================================================

# base_case = f"generated_cases/{case_name}"

# template_path = "templates/base_case"

# # =====================================================
# # CREATE CASE FROM TEMPLATE
# # =====================================================

# if os.path.exists(base_case):
#     shutil.rmtree(base_case)

# shutil.copytree(template_path, base_case)

# print("Base case copied!")

# # =====================================================
# # STL OUTPUT PATHS
# # =====================================================

# tri_surface = f"{base_case}/constant/triSurface"

# tank_stl = f"{tri_surface}/vessel.stl"

# impeller_stl = f"{tri_surface}/impeller.stl"

# # =====================================================
# # GENERATE TANK
# # =====================================================

# generate_tank(
#     tank_radius=tank_radius,
#     tank_height=tank_height,
#     wall_thickness=wall_thickness,
#     bottom_thickness=bottom_thickness,
#     output_path=tank_stl
# )

# # =====================================================
# # GENERATE IMPELLER
# # =====================================================

# generate_impeller(
#     tank_height=tank_height,

#     shaft_radius=shaft_radius,
#     shaft_height=shaft_height,

#     hub_radius=hub_radius,
#     hub_height=hub_height,
#     hub_z=hub_z,

#     blade_length=blade_length,
#     blade_width=blade_width,
#     blade_thickness=blade_thickness,

#     num_blades=num_blades,
#     pitch_angle=pitch_angle,

#     output_path=impeller_stl
# )

# print("Geometry generated!")

# # =====================================================
# # RUN OPENFOAM COMMANDS
# # =====================================================

# # case_path = os.path.abspath(base_case)

# # print("Running blockMesh...")

# # subprocess.run(
# #     ["blockMesh"],
# #     cwd=case_path
# # )

# # print("Running surfaceFeatureExtract...")

# # subprocess.run(
# #     ["surfaceFeatureExtract"],
# #     cwd=case_path
# # )

# # print("Running snappyHexMesh...")

# # subprocess.run(
# #     ["snappyHexMesh", "-overwrite"],
# #     cwd=case_path
# # )

# # print("Meshing complete!")

# # =====================================================
# # RUN OPENFOAM COMMANDS
# # =====================================================

# # =====================================================
# # RUN OPENFOAM COMMANDS
# # =====================================================

# case_path = os.path.abspath(base_case)

# def run_cmd(cmd):
#     print(f"\nRunning: {' '.join(cmd)}")
#     result = subprocess.run(cmd, cwd=case_path)

#     if result.returncode != 0:
#         raise RuntimeError(f"Command failed: {' '.join(cmd)}")

# # Clean old mesh from template
# poly_mesh = os.path.join(case_path, "constant", "polyMesh")
# if os.path.exists(poly_mesh):
#     shutil.rmtree(poly_mesh)

# run_cmd(["blockMesh"])
# run_cmd(["surfaceFeatureExtract"])
# run_cmd(["snappyHexMesh", "-overwrite"])
# run_cmd(["checkMesh"])

# # Run solver
# # run_cmd(["simpleFoam"])

# # Create ParaView file
# open(os.path.join(case_path, "case.foam"), "a").close()

# print("\nSimulation complete!")
# print(f"Open with: paraview {case_path}/case.foam")

import os
import re
import shutil
import subprocess
import math

from tank_builder import generate_tank
from impeller_builder import generate_impeller


def run_case(params):
    case_name = params["case_name"]

    tank_radius = params["tank_radius"]
    tank_height = params["tank_height"]

    wall_thickness = params.get("wall_thickness", 0.01)
    bottom_thickness = params.get("bottom_thickness", 0.01)

    shaft_radius = params["shaft_radius"]
    shaft_height = params["shaft_height"]

    hub_radius = params["hub_radius"]
    hub_height = params["hub_height"]
    hub_z = params["hub_z"]

    blade_length = params["blade_length"]
    blade_width = params["blade_width"]
    blade_thickness = params["blade_thickness"]

    num_blades = params["num_blades"]
    pitch_angle = params["pitch_angle"]
    rpm = params["rpm"]

    mesh_cells_x = params["mesh_cells_x"]
    mesh_cells_y = params["mesh_cells_y"]
    mesh_cells_z = params["mesh_cells_z"]
    block_padding = params["block_padding"]

    tank_diameter = 2 * tank_radius
    impeller_radius = hub_radius + blade_length
    impeller_diameter = 2 * impeller_radius

    mrf_radius = impeller_radius * 1.3
    mrf_half_height = 0.07

    mrf_z_min = hub_z - mrf_half_height
    mrf_z_max = hub_z + mrf_half_height

    omega = rpm * 2 * math.pi / 60

    x_min = -tank_radius - block_padding
    x_max = tank_radius + block_padding

    y_min = -tank_radius - block_padding
    y_max = tank_radius + block_padding

    z_min = -block_padding
    z_max = tank_height + block_padding

    temperature = params["temperature"]
    density = params["density"]
    viscosity = params["viscosity"]

    kinematic_viscosity = viscosity / density
    

    if impeller_diameter >= tank_diameter:
        raise ValueError("Impeller diameter must be smaller than tank diameter.")

    if mrf_radius >= tank_radius:
        raise ValueError("MRF radius must be smaller than tank radius.")

    if shaft_height > tank_height:
        raise ValueError("Shaft height cannot exceed tank height.")

    if mrf_z_min < 0 or mrf_z_max > tank_height:
        raise ValueError("MRF region must stay inside tank height.")

    base_case = f"generated_cases/{case_name}"
    template_path = "templates/base_case"

    if os.path.exists(base_case):
        shutil.rmtree(base_case)

    shutil.copytree(template_path, base_case)

    print("Base case copied!")

    tri_surface = f"{base_case}/constant/triSurface"

    generate_tank(
        tank_radius=tank_radius,
        tank_height=tank_height,
        wall_thickness=wall_thickness,
        bottom_thickness=bottom_thickness,
        output_path=f"{tri_surface}/vessel.stl"
    )

    generate_impeller(
        tank_height=tank_height,
        shaft_radius=shaft_radius,
        shaft_height=shaft_height,
        hub_radius=hub_radius,
        hub_height=hub_height,
        hub_z=hub_z,
        blade_length=blade_length,
        blade_width=blade_width,
        blade_thickness=blade_thickness,
        num_blades=num_blades,
        pitch_angle=pitch_angle,
        output_path=f"{tri_surface}/impeller.stl"
    )

    print("Geometry generated!")

    block_mesh_dict = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM                                      |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    ({x_min} {y_min} {z_min})
    ({x_max} {y_min} {z_min})
    ({x_max} {y_max} {z_min})
    ({x_min} {y_max} {z_min})
    ({x_min} {y_min} {z_max})
    ({x_max} {y_min} {z_max})
    ({x_max} {y_max} {z_max})
    ({x_min} {y_max} {z_max})
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({mesh_cells_x} {mesh_cells_y} {mesh_cells_z}) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    allBoundary
    {{
        type patch;
        faces
        (
            (0 4 7 3)
            (1 2 6 5)
            (0 1 5 4)
            (3 7 6 2)
            (0 3 2 1)
        );
    }}

    top
    {{
        type symmetry;
        faces
        (
            (4 5 6 7)
        );
    }}
);
"""

    with open(f"{base_case}/system/blockMeshDict", "w") as f:
        f.write(block_mesh_dict)

    print("blockMeshDict written!")

    snappy_path = f"{base_case}/system/snappyHexMeshDict"

    with open(snappy_path, "r") as f:
        snappy = f.read()

    start = snappy.find("MRF\n    {")
    end = snappy.find("}", start) + 1

    new_mrf_block = f"""MRF
    {{
        type searchableCylinder;
        point1 (0 0 {mrf_z_min});
        point2 (0 0 {mrf_z_max});
        radius {mrf_radius};
    }}"""

    snappy = snappy[:start] + new_mrf_block + snappy[end:]

    snappy = re.sub(
        r"locationInMesh\s*\([^;]+\);",
        f"locationInMesh (0.05 0.05 {tank_height / 2});",
        snappy
    )

    with open(snappy_path, "w") as f:
        f.write(snappy)

    print("snappyHexMeshDict updated!")

    mrf_properties = f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM                                      |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      MRFProperties;
}}

MRF1
{{
    cellZone    cellMRFzone;

    active      yes;

    nonRotatingPatches ();

    origin      (0 0 {hub_z});
    axis        (0 0 1);
    omega       {omega};
}}
"""
    transport_properties = f"""/*--------------------------------*- C++ -*----------------------------------*\\
    | =========                 |                                                 |
    | \\\\      /  F ield         | OpenFOAM                                      |
    \\*---------------------------------------------------------------------------*/
    FoamFile
    {{
        version     2.0;
        format      ascii;
        class       dictionary;
        object      transportProperties;
    }}

    transportModel  Newtonian;

    nu              [0 2 -1 0 0 0 0] {kinematic_viscosity};
    rho             [1 -3 0 0 0 0 0] {density};
    temperature     [0 0 0 1 0 0 0] {temperature};
    """

    with open(f"{base_case}/constant/transportProperties", "w") as f:
        f.write(transport_properties)

    print("transportProperties written!")

    with open(f"{base_case}/constant/MRFProperties", "w") as f:
        f.write(mrf_properties)

    print("MRFProperties written!")

    case_path = os.path.abspath(base_case)

    print("Running blockMesh...")
    subprocess.run(["blockMesh"], cwd=case_path, check=True)

    print("Running surfaceFeatureExtract...")
    subprocess.run(["surfaceFeatureExtract"], cwd=case_path, check=True)

    print("Running snappyHexMesh...")
    result = subprocess.run(["snappyHexMesh", "-overwrite"], cwd=case_path)

    if result.returncode != 0:
        print("WARNING: snappyHexMesh reported mesh quality problems.")
        print("Continuing to simpleFoam anyway...")

    # print("Running simpleFoam...")
    # subprocess.run(["simpleFoam"], cwd=case_path, check=True)

    print("Running simpleFoam...")

    log_path = os.path.join(case_path, "log.simpleFoam")

    with open(log_path, "w") as log:
        process = subprocess.Popen(
            ["simpleFoam"],
            cwd=case_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in process.stdout:
            print(line, end="")
            log.write(line)
            log.flush()

        process.wait()

        if process.returncode != 0:
            raise RuntimeError("simpleFoam failed.")

    print("Meshing and simulation complete!")

    print("Running post-processing...")
    subprocess.run(
        ["python3", "post_process.py", case_path],
        check=True
    )

    print("Full pipeline complete!")

if __name__ == "__main__":
    default_params = {
        "case_name": "case_002",

        "tank_radius": 0.37,
        "tank_height": 0.5,

        "shaft_radius": 0.008,
        "shaft_height": 0.4,

        "hub_radius": 0.04,
        "hub_height": 0.03,
        "hub_z": 0.28,

        "blade_length": 0.07,
        "blade_width": 0.04,
        "blade_thickness": 0.006,

        "num_blades": 4,
        "pitch_angle": 30,
        "rpm": 300,

        "mesh_cells_x": 45,
        "mesh_cells_y": 45,
        "mesh_cells_z": 95,
        "block_padding": 0.05,

        "temperature": 280,
        "density": 800,
        "viscosity": 0.6,
    }

    run_case(default_params)