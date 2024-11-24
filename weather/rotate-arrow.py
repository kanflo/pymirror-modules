#!/usr/bin/env python3

# A script for creating rotated copies of the wind direction arrow

import sys
from subprocess import call


if len(sys.argv) != 7:
    print("Usage: %s <arrow file name> <destination path> <initial angle> <steps> <width> <height>" % sys.argv[0])
    print("  <arrow file name>   Name of starting arrow")
    print("  <destination path>  Path where rotations will be saved")
    print("  <initial angle>     Where your arrow is pointing")
    print("  <steps>             Rotation steps")
    print("  <width> <height>    Uniform size of output images")
    print(" Eg. %s arrow.png arrows/ 0 22.5 400 400" % sys.argv[0])
    sys.exit(1)

arrow = sys.argv[1]
base_name = arrow.split(".")[0]
extension = arrow.split(".")[1]
output = sys.argv[2]
initial_angle = float(sys.argv[3])
steps = float(sys.argv[4])
width = int(sys.argv[5])
height = int(sys.argv[6])

for i in range(360//int(steps)):
    angle = initial_angle + steps * i
    if angle > 360:
        angle -= 360
    print("  %.1f" % (angle))
    cmd = "convert -background none -rotate %.2f -gravity center -extent %dx%d %s %s/%s-%04d.%s" % (angle, width, height, arrow, output, base_name, 10*angle, extension)
    call(cmd.split(" "))
