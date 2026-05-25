# import cadquery as cq

# def generate_tank(
#     tank_radius,
#     tank_height,
#     wall_thickness,
#     bottom_thickness,
#     output_path
# ):

#     inner_radius = tank_radius - wall_thickness

#     # Outer tank
#     outer = (
#         cq.Workplane("XY")
#         .circle(tank_radius)
#         .extrude(tank_height)
#     )

#     # Inner hollow region
#     inner = (
#         cq.Workplane("XY")
#         .workplane(offset=bottom_thickness)
#         .circle(inner_radius)
#         .extrude(tank_height)
#     )

#     # Hollow tank
#     tank = outer.cut(inner)

#     # Export STL
#     cq.exporters.export(tank, output_path)

#     print("Tank STL generated!")


# # =====================================================
# # TEST RUN
# # =====================================================

# if __name__ == "__main__":

#     generate_tank(
#         tank_radius=0.2,
#         tank_height=0.5,
#         wall_thickness=0.01,
#         bottom_thickness=0.01,
#         output_path="tank.stl"
#     )

import cadquery as cq

def generate_tank(
    tank_radius,
    tank_height,
    wall_thickness,
    bottom_thickness,
    output_path
):
    # Solid tank / solid cylinder
    tank = (
        cq.Workplane("XY")
        .circle(tank_radius)
        .extrude(tank_height)
    )

    # Export STL
    cq.exporters.export(tank, output_path)

    print("Solid tank STL generated!")


# =====================================================
# TEST RUN
# =====================================================

if __name__ == "__main__":

    generate_tank(
        tank_radius=0.3,
        tank_height=0.7,
        wall_thickness=0.01,
        bottom_thickness=0.01,
        output_path="tank.stl"
    )