# Generates a planet using perlin noise and a
# serial string from the Traveler 2nd edition
import perlin2d as perlin
import numpy as np
from PIL import Image


# Constants

# Helper functions


# Create a detailed perlin array
width = 500
height = 500
detail = 3
octave = 8

perlin2d_array = perlin.perlin2d(width, height, detail, octave)



# TODO: Depending on geology use different sets of colors
# TODO: Depending on planet size change the radius
# TODO: Depending on atmosphear add an outer radious representing the "Size"
# TODO: Depending on population 


# Scale every point up by 255 (0-255 for white levels in an image array)
formatted = (perlin2d_array * 255).astype('uint8')

# Use Pillow to create an image
img = Image.fromarray(formatted)
img.show()