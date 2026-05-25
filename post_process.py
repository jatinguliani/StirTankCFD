import os
import re
import csv
import subprocess
import numpy as np
import matplotlib.pyplot as plt
import pyvista as pv


def get_latest_time(case_path):
    times = []
    for item in os.listdir(case_path):
        path = os.path.join(case_path, item)
        if os.path.isdir(path):
            try:
                times.append(float(item))
            except ValueError:
                pass

    if not times:
        raise RuntimeError("No simulation time folders found.")

    latest = max(times)
    return str(int(latest)) if latest.is_integer() else str(latest)


def read_internal_field_vector(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    match = re.search(
        r"internalField\s+nonuniform\s+List<vector>\s+\d+\s*\((.*?)\)\s*;",
        text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError(f"Could not read vector field: {file_path}")

    vectors = re.findall(
        r"\(([-+eE0-9\.]+)\s+([-+eE0-9\.]+)\s+([-+eE0-9\.]+)\)",
        match.group(1),
    )

    return np.array(vectors, dtype=float)


def read_internal_field_scalar(file_path):
    with open(file_path, "r") as f:
        text = f.read()

    match = re.search(
        r"internalField\s+nonuniform\s+List<scalar>\s+\d+\s*\((.*?)\)\s*;",
        text,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError(f"Could not read scalar field: {file_path}")

    values = re.findall(r"[-+eE0-9\.]+", match.group(1))
    return np.array(values, dtype=float)


def make_summary_csv(output_dir, latest_time, velocity_mag, pressure):
    csv_path = os.path.join(output_dir, "summary.csv")

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["quantity", "value", "unit"])
        writer.writerow(["latest_time", latest_time, "iteration/time"])
        writer.writerow(["cells", len(velocity_mag), "-"])
        writer.writerow(["average_velocity", velocity_mag.mean(), "m/s"])
        writer.writerow(["maximum_velocity", velocity_mag.max(), "m/s"])
        writer.writerow(["minimum_pressure", pressure.min(), "OpenFOAM pressure unit"])
        writer.writerow(["maximum_pressure", pressure.max(), "OpenFOAM pressure unit"])


def make_summary_plot(output_dir, velocity_mag, pressure):
    labels = ["Avg Velocity", "Max Velocity", "Min Pressure", "Max Pressure"]
    values = [velocity_mag.mean(), velocity_mag.max(), pressure.min(), pressure.max()]

    plt.figure()
    plt.bar(labels, values)
    plt.xticks(rotation=20)
    plt.title("CFD Summary")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "summary_plot.png"), dpi=200)
    plt.close()


def make_residual_plot(case_path, output_dir):
    log_path = os.path.join(case_path, "log.simpleFoam")

    if not os.path.exists(log_path):
        print("No log.simpleFoam found. Skipping residual plot.")
        return

    residuals = {}

    with open(log_path, "r", errors="ignore") as f:
        for line in f:
            match = re.search(
                r"Solving for (\w+), Initial residual = ([eE0-9.+-]+)",
                line
            )

            if match:
                field = match.group(1)
                value = float(match.group(2))
                residuals.setdefault(field, []).append(value)

    if not residuals:
        print("No residuals found. Skipping residual plot.")
        return

    fields = list(residuals.keys())
    max_len = max(len(v) for v in residuals.values())

    with open(os.path.join(output_dir, "residuals.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["iteration"] + fields)

        for i in range(max_len):
            row = [i + 1]
            for field in fields:
                row.append(residuals[field][i] if i < len(residuals[field]) else "")
            writer.writerow(row)

    plt.figure()
    for field, values in residuals.items():
        plt.semilogy(range(1, len(values) + 1), values, label=field)

    plt.xlabel("Iteration")
    plt.ylabel("Initial Residual")
    plt.title("Solver Residuals")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "residuals.png"), dpi=200)
    plt.close()


def convert_to_vtk(case_path):
    subprocess.run(["foamToVTK"], cwd=case_path, check=True)


def find_latest_vtu(case_path):
    vtk_dir = os.path.join(case_path, "VTK")

    if not os.path.exists(vtk_dir):
        raise RuntimeError("VTK folder not found.")

    vtu_files = []

    for root, dirs, files in os.walk(vtk_dir):
        for file in files:
            if file == "internal.vtu":
                vtu_files.append(os.path.join(root, file))

    if not vtu_files:
        raise RuntimeError("No internal.vtu file found.")

    def extract_time(path):
        folder = os.path.basename(os.path.dirname(path))
        try:
            return float(folder.split("_")[-1])
        except ValueError:
            return -1

    return sorted(vtu_files, key=extract_time)[-1]


def make_pyvista_outputs(case_path, output_dir):
    convert_to_vtk(case_path)

    vtu_path = find_latest_vtu(case_path)
    mesh = pv.read(vtu_path)

    if "U" not in mesh.array_names:
        raise RuntimeError("Velocity field U not found in VTK file.")

    mesh["Velocity Magnitude"] = np.linalg.norm(mesh["U"], axis=1)

    # Velocity PNG
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(mesh, scalars="Velocity Magnitude", show_edges=False)
    plotter.add_scalar_bar("Velocity Magnitude")
    plotter.view_isometric()
    plotter.screenshot(os.path.join(output_dir, "velocity_contour.png"))
    plotter.close()

    # Pressure PNG
    if "p" in mesh.array_names:
        plotter = pv.Plotter(off_screen=True)
        plotter.add_mesh(mesh, scalars="p", show_edges=False)
        plotter.add_scalar_bar("Pressure")
        plotter.view_isometric()
        plotter.screenshot(os.path.join(output_dir, "pressure_contour.png"))
        plotter.close()

    # Velocity rotation GIF
    gif_path = os.path.join(output_dir, "velocity_rotation.gif")

    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(mesh, scalars="Velocity Magnitude", show_edges=False)
    plotter.add_scalar_bar("Velocity Magnitude")
    plotter.view_isometric()

    plotter.open_gif(gif_path)

    for _ in range(36):
        plotter.camera.Azimuth(10)
        plotter.render()
        plotter.write_frame()

    plotter.close()

    print(f"GIF saved to: {gif_path}")
def post_process(case_path):
    latest_time = get_latest_time(case_path)

    output_dir = os.path.join(case_path, "postProcessingResults")
    os.makedirs(output_dir, exist_ok=True)

    u_path = os.path.join(case_path, latest_time, "U")
    p_path = os.path.join(case_path, latest_time, "p")

    U = read_internal_field_vector(u_path)
    p = read_internal_field_scalar(p_path)
    velocity_mag = np.linalg.norm(U, axis=1)

    print("\n===== POST-PROCESSING SUMMARY =====")
    print(f"Latest time: {latest_time}")
    print(f"Cells read: {len(velocity_mag)}")
    print(f"Average velocity: {velocity_mag.mean():.6f} m/s")
    print(f"Maximum velocity: {velocity_mag.max():.6f} m/s")
    print(f"Minimum pressure: {p.min():.6f}")
    print(f"Maximum pressure: {p.max():.6f}")
    print("===================================\n")

    make_summary_csv(output_dir, latest_time, velocity_mag, p)
    make_summary_plot(output_dir, velocity_mag, p)
    make_residual_plot(case_path, output_dir)

    try:
        make_pyvista_outputs(case_path, output_dir)
    except Exception as e:
        print(f"PyVista/VTK visualization skipped: {e}")

    print(f"Plots saved to: {output_dir}")


if __name__ == "__main__":
    import sys

    case_path = sys.argv[1] if len(sys.argv) > 1 else "generated_cases/case_002"
    post_process(case_path)