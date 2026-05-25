import cadquery as cq

def generate_impeller(
    tank_height,
    shaft_radius,
    shaft_height,
    hub_radius,
    hub_height,
    hub_z,
    blade_length,
    blade_width,
    blade_thickness,
    num_blades,
    pitch_angle,
    output_path
):

    # =====================================================
    # VALIDATION
    # =====================================================

    if shaft_height > tank_height:
        raise ValueError(
            "Shaft height cannot exceed tank height"
        )

    # =====================================================
    # CREATE SHAFT
    # =====================================================

    shaft_bottom = hub_z + hub_height / 2
    shaft_top = shaft_height
    shaft_length = shaft_top - shaft_bottom

    shaft = (
        cq.Workplane("XY")
        .circle(shaft_radius)
        .extrude(shaft_length)
        .translate((0, 0, shaft_bottom))
    )

    # =====================================================
    # CREATE HUB
    # =====================================================

    hub = (
        cq.Workplane("XY")
        .circle(hub_radius)
        .extrude(hub_height)
        .translate((0, 0, hub_z - hub_height / 2))
    )

    impeller = shaft.union(hub)

    # =====================================================
    # CREATE BLADES
    # =====================================================

# =====================================================
# CREATE BLADES
# =====================================================

    blades = []
    num_blades = 4

    for i in range(num_blades):

        angle = i * 360 / num_blades
        blade_overlap = 0.1 * blade_length

        blade = (
            cq.Workplane("XY")
            .box(
                blade_length,
                blade_width,
                blade_thickness
            )
            .rotate((0, 0, 0), (1, 0, 0), pitch_angle)
            .translate(
                (
                    hub_radius + blade_length / 2 - blade_overlap / 2,
                    0,
                    hub_z
                )
            )
            .rotate((0, 0, 0), (0, 0, 1), angle)
        )

        blades.append(blade)

    for blade in blades:
        impeller = impeller.union(blade)

    # =====================================================
    # EXPORT STL
    # =====================================================

    cq.exporters.export(
        impeller,
        output_path
    )

    print("Impeller STL generated!")


# =====================================================
# TEST RUN
# =====================================================

if __name__ == "__main__":

    generate_impeller(
        tank_height=0.7,

        shaft_radius=0.008,
        shaft_height=0.485,

        hub_radius=0.04,
        hub_height=0.03,
        hub_z=0.1,

        blade_length=0.1,
        blade_width=0.04,
        blade_thickness=0.006,

        num_blades=4,
        pitch_angle=30,

        output_path="impeller.stl"
    )