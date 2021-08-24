# Creates the tools returning 2D-perlin noise
import math
import random
import numpy as np
from PIL import Image


# Helper class
class Vector2d:
    """ A 2d vector objects holding an X and Y value.
    """
    def __init__(self, Coordinates):
        self.x = Coordinates[0]
        self.y = Coordinates[1]

# Helper functions

# Returns the dotprocut of two vectors.
def getdotproduct(vector1, vector2):
    """Takes two vectors as inteable objects and returns the caluclated.
    Dot product of the two. The vectors must be of equal dimension or an
    Exception is raised.

    Args:
        vector1 (iterable list): Vector 1
        vector2 (iterable list): Vector 2

    Raises:
        Exception: If vectors are not of equal dimension an error is raised.

    Returns:
        float: Returns the dot product of the two vectors
    """
    if len(vector1) != len(vector2):
        raise Exception('Vectors are not of equal dimension')
    
    product = 0.0
    for n in range(len(vector1)):
        product += vector1[n]*vector2[n]
    
    return product

# Smooth a value with 6t⁵-15t⁴+10t³
def fade(t: float) -> float:
    """fade(t) = 6t⁵-15t⁴+10t³
    Smoothing function for the interpolation fractions. This is to prevent
    a repeated "box" pattern in the perlin noise.

    Args:
        t (float): The fractional X or Y value to be faded/smoothed

    Returns:
        float: The smoothed value
    """
    return (t*t*t*(t*(t*6-15)+10))


# Interpolate (Lerp)
def mylerp(d1:float, d2:float, d3:float, d4:float, fracx: float, fracy: float) -> float:
    """Takes four dot products and applies linear interpolation between them.

    Args:
        d1 (float): Dot product one
        d2 (float): Dot product two
        d3 (float): Dot product three
        d4 (float): Dot product four
        fracx (float): [Weight of which X value to take the majority from]
        fracy (float): [Weight if which Y value to take the majority from]

    Returns:
        float: [The interpolation of the four dot products]
    """
    d13 = d1+fracx*(d3-d1)
    d24 = d2+fracx*(d4-d2)
    d = d13+fracy*(d24-d13)
    return d


# Create a gradient vector permutation grid
sqrt_2 = math.sqrt(2)
perm_table = [(-1/sqrt_2,-1/sqrt_2), (-1,0), (-1/sqrt_2,1/sqrt_2), (0,-1), (0,1), (1/sqrt_2,-1/sqrt_2),(1,0),(1/sqrt_2,1/sqrt_2)]

#fill a vector table
vect_table = []
for perm in perm_table:
    vect_table.append(Vector2d(perm))


def perlin2d(width:int, height:int, detail:int = 1, octaves:int =1):
    """Creates an array of perlin noise with set dimensions and detail.

    Args:
        width (int): Width of the returned array
        height (int): Height of the returned array
        detail (int, optional): Higher means higher frequency. Defaults to 1.
        octaves (int, optional): Gives a fractal look. Defaults to 1.

    Returns:
        [Array]: [Numpy array of perlin noise values between 0-1]
    """
    detail = detail*0.001
    noisearray = np.zeros((width, height))

    # Create a 2D gradient grid with random vectors from the permutation table
    grid_width = math.ceil(width * detail * (2**octaves))
    grid_height = math.ceil(height * detail * (2**octaves))
    gradient_vector_grid = []

    for x in range(grid_width+1):
        temp = []

        for y in range(grid_height+1):
            temp.append(random.choice(vect_table))
        gradient_vector_grid.append(temp)

    for oct in range(1,octaves+1):
        effect = 1/2**oct
        step = detail * 2**oct
        for x in range(width):
            for y in range(height):
                # Get the four surrounding vectors      - OBS needs to be e.g. x*step floored
                x1 = math.floor(x*step)
                y1 = math.floor(y*step)
                v1 = gradient_vector_grid[x1][y1]
                v2 = gradient_vector_grid[x1][y1+1]
                v3 = gradient_vector_grid[x1+1][y1]
                v4 = gradient_vector_grid[x1+1][y1+1]

                # Get the distance vectors
                dist1 = (x*step%1, y*step%1)
                dist2 = (x*step%1, y*step%1-1)
                dist3 = (x*step%1-1, y*step%1)
                dist4 = (x*step%1-1, y*step%1-1)

                # Get the dot procuct for each point withing the vectors
                dot1 = getdotproduct((v1.x,v1.y), dist1)
                dot2 = getdotproduct((v2.x,v2.y), dist2)
                dot3 = getdotproduct((v3.x,v3.y), dist3)
                dot4 = getdotproduct((v4.x,v4.y), dist4)

                # Interpolate the points but fade the fractional distances.
                fractionx = fade(x*step%1)
                fractiony = fade(y*step%1)

                point = mylerp(dot1, dot2, dot3, dot4, fractionx, fractiony)

                noisearray[x][y] += point * effect

    # Changing values from -1 to 1 to 0-1.
    # This can be done by increasing value by 1 and dividing by 2.
    for x in range(width):
        for y in range(height):
            noisearray[x][y] += 1
            noisearray[x][y] /= 2

    return noisearray

if __name__ == "__main__":
    # Generation settings
    width = 1000
    height = 1000
    detail = 1
    octave = 4

    perlin2d_array = perlin2d(width, height, detail, octave)

    # Scale every point up by 255 (0-255 for white levels in an image array)
    formatted = (perlin2d_array * 255).astype('uint8')

    # Use Pillow to create an image
    img = Image.fromarray(formatted)
    img.show()