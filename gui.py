# import sys
# from PyQt6.QtWidgets import (
#     QApplication,
#     QWidget,
#     QLabel,
#     QLineEdit,
#     QPushButton,
#     QGridLayout,
#     QTextEdit,
# )

# from case_builder import run_case


# class TankCFDGui(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Tank CFD App")

#         self.inputs = {}

#         layout = QGridLayout()

#         fields = {
#             "case_name": "case_gui_001",

#             "tank_radius": "0.30",
#             "tank_height": "0.70",

#             "shaft_radius": "0.008",
#             "shaft_height": "0.65",

#             "hub_radius": "0.04",
#             "hub_height": "0.03",
#             "hub_z": "0.28",

#             "blade_length": "0.07",
#             "blade_width": "0.04",
#             "blade_thickness": "0.006",

#             "num_blades": "4",
#             "pitch_angle": "30",
#             "rpm": "300",

#             "mesh_cells_x": "45",
#             "mesh_cells_y": "45",
#             "mesh_cells_z": "95",
#             "block_padding": "0.05",
#         }

#         row = 0

#         for key, default in fields.items():
#             label = QLabel(key)
#             input_box = QLineEdit(default)

#             self.inputs[key] = input_box

#             layout.addWidget(label, row, 0)
#             layout.addWidget(input_box, row, 1)

#             row += 1

#         self.run_button = QPushButton("Generate Mesh + Run Simulation")
#         self.run_button.clicked.connect(self.run_simulation)

#         layout.addWidget(self.run_button, row, 0, 1, 2)

#         row += 1

#         self.log_box = QTextEdit()
#         self.log_box.setReadOnly(True)

#         layout.addWidget(self.log_box, row, 0, 1, 2)

#         self.setLayout(layout)

#     def get_params(self):
#         params = {}

#         for key, input_box in self.inputs.items():
#             value = input_box.text()

#             if key == "case_name":
#                 params[key] = value
#             elif key in ["num_blades", "mesh_cells_x", "mesh_cells_y", "mesh_cells_z"]:
#                 params[key] = int(value)
#             else:
#                 params[key] = float(value)

#         return params

#     def run_simulation(self):
#         self.log_box.append("Starting CFD pipeline...")

#         try:
#             params = self.get_params()
#             run_case(params)
#             self.log_box.append("Pipeline complete!")

#         except Exception as e:
#             self.log_box.append(f"ERROR: {e}")


# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     window = TankCFDGui()
#     window.show()

#     sys.exit(app.exec())


import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QGridLayout, QTextEdit

from case_builder import run_case


class CFDWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, params):
        super().__init__()
        self.params = params

    def run(self):
        try:
            run_case(self.params)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class TankCFDGui(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tank CFD App")
        self.inputs = {}

        layout = QGridLayout()

        fields = {
            "case_name": ("case_gui_001", "-"),
            "tank_radius": ("0.30", "m"),
            "tank_height": ("0.70", "m"),
            "shaft_radius": ("0.008", "m"),
            "shaft_height": ("0.65", "m"),
            "hub_radius": ("0.04", "m"),
            "hub_height": ("0.03", "m"),
            "hub_z": ("0.28", "m"),
            "blade_length": ("0.07", "m"),
            "blade_width": ("0.04", "m"),
            "blade_thickness": ("0.006", "m"),
            "num_blades": ("4", "count"),
            "pitch_angle": ("30", "deg"),
            "rpm": ("300", "rev/min"),
            "mesh_cells_x": ("45", "cells"),
            "mesh_cells_y": ("45", "cells"),
            "mesh_cells_z": ("95", "cells"),
            "block_padding": ("0.05", "m"),
            "temperature": ("298", "K"),
            "density": ("1000", "kg/m³"),
            "viscosity": ("0.001", "Pa·s"),
        }

        row = 0
        for key, (default, unit) in fields.items():
            self.inputs[key] = QLineEdit(default)

            layout.addWidget(QLabel(key), row, 0)
            layout.addWidget(self.inputs[key], row, 1)
            layout.addWidget(QLabel(unit), row, 2)

            row += 1

        self.run_button = QPushButton("Generate Mesh + Run Simulation")
        self.run_button.clicked.connect(self.run_simulation)
        layout.addWidget(self.run_button, row, 0, 1, 2)

        row += 1
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        layout.addWidget(self.log_box, row, 0, 1, 2)

        self.setLayout(layout)

    def get_params(self):
        params = {}
        for key, input_box in self.inputs.items():
            value = input_box.text()

            if key == "case_name":
                params[key] = value
            elif key in ["num_blades", "mesh_cells_x", "mesh_cells_y", "mesh_cells_z"]:
                params[key] = int(value)
            else:
                params[key] = float(value)

        return params

    def run_simulation(self):
        self.log_box.append("Starting CFD pipeline...")
        self.run_button.setEnabled(False)

        try:
            params = self.get_params()

            self.worker = CFDWorker(params)

            self.worker.finished.connect(self.simulation_finished)
            self.worker.error.connect(self.simulation_error)

            self.worker.start()

        except Exception as e:
            self.log_box.append(f"ERROR: {e}")
            self.run_button.setEnabled(True)

    def simulation_finished(self):
        self.log_box.append("Pipeline complete!")
        self.run_button.setEnabled(True)

    def simulation_error(self, message):
        self.log_box.append(f"ERROR: {message}")
        self.run_button.setEnabled(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TankCFDGui()
    window.show()
    sys.exit(app.exec())