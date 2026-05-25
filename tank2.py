import cadquery as cq

# Parameters
radius = 0.2
height = 0.5

# Create solid cylinder
tank = (
    cq.Workplane("XY")
    .circle(radius)
    .extrude(height)
)

# Export STL
cq.exporters.export(tank, "solid_tank.stl")

print("Solid tank STL generated!")