# Generates a planet using perlin noise and a
# serial string from the Traveler 2nd edition
import perlin2d as perlin
import numpy as np
import random
from PIL import Image


# Constants
colors = {  'water':        [0, 128, 255],
            'forest':       [0, 204, 0],
            'sand':         [255, 227, 112],
            'mountain':     [128, 128, 128]}

# Helper functions
def color_array(height_array, color_palette):
    """Takes an array with perlin noise and adds color based on the color and height
    value in the color palette

    Args:
        height_array (np.ndarray): Numpy array with perlin noise between 0-1
        color_palette (List): List with dictionary elements.

    Raises:
        ValueError: If the height_array is not an numpy array throw a ValueError exception.

    Returns:
        [ndarray]: numpy array containing RBG information.
    """

    # Check that data type is correct
    if not isinstance(height_array, np.ndarray):
        raise TypeError('The provided array is not a numpy array.')

    # Create an empty copy of array
    array_colored = np.zeros(height_array.shape + (3,))
    height_lower_limit = 0

    for color, height_upper_limit in color_palette:
        for x, y in height_array.shape:
            if height_array[x][y] <= height_upper_limit and height_array[x][y] > height_lower_limit:
                array_colored[x][y] = color

        height_lower_limit += height_upper_limit
    
    return array_colored


def create_color_palette(upp_dict):
    # Ensure the upp_dict is a dictionary
    if not isinstance(upp_dict, dict):
        raise TypeError('The provided variable is not a dictionary.')
    palette = {}
    # Different levels in every palette
    # Water, Sand, Land, Mountain, mountain top, atmosphere
    # 1. Determine sea type and level
    #   1.a Could be canyons with depth instead
    #   1.b Or lava if dry and hot

    # 2. Determine sandlevel
    # 3. Determine Landtype and level
    # 4. Determine mountain color and level
    # 5. Determine mountain tops if any
    # 6. Determine color of atmosphere
    #       blue is breathable, (different alpha levels for thin, standard, dense)

    # Examples
    # Earthlike
    #   level 6 standard atmosphere
    #   level 7 66-75% hydrographic level Earth-like
    #   level 5-9 temperature (temperate)
    #   size 8

    # mars like
    #   size 5
    #   level 1 trace atmosphere
    #   level 0 0-5% hydrograhpic level - dessert world
    #   level 0 temperature frigid world
    pass


def upp_to_dict(upp_string):
    """Takes an Universal Planetary Profile string (UPP string) and converts
    it into a dictionary. The values are taken from the UPP and the keys are the following: 
    UPP (Universal Planetary Profile)
    Starport quality A,B,C,D,E and X
    Size 1-A
    Atmosphere type 0-F
    Hydrographic percentage 0-A
    Population 0-C
    Goverment type 0-F
    Law level 0-F
    Tech level 0-F
    Temperature 0-4
    Observe that temperature is no included in the upp-string but calculated randomly 
    in conjuntion with atmosphere
    Example. Earth = A867949-D

    Args:
        upp_string (string): UPP string containing hexadecimal values

    Raises:
        ValueError: If the provided upp_string is not of type string.

    Returns:
        dictionary: A dictionary that has paired the different names with the values in the docstring. See
        description
    """

    if not isinstance(upp_string, str):
        raise TypeError('An UPP string must be of type string.')
    
    # remove the hyphen between law and tech level
    upp_string.replace('-', '')

    # Create a ditionary with name and int value pairs.
    upp_variables = [   'starport_quality',
                        'size',
                        'atmosphere_type',
                        'hydrographic_percentage',
                        'population',
                        'government_type',
                        'law_level',
                        'tech_level']
    
    upp_dict = {}
    for variable_name, upp_value in zip(upp_variables, upp_string):
        upp_dict.update({variable_name : int(upp_value, 16)})
    
    # Moongose traveler 2e Core rulebook P.219 generate temperature by rolling two six sided die
    # and adding a modifier provided by planetary atmosphere (corresponding tothe dictionary below) 
    
    temperature_modifier = {0: 0,
                            1: 0,
                            2: -2,
                            3: -2,
                            4: -1,
                            5: -1,
                            6: 0,
                            7: 0,
                            8: 1,
                            9: 1,
                            10: 2,
                            11: 6,
                            12: 6,
                            13: 2,
                            14: -1,
                            15: 2}

    dice = random.randint(1,6)
    dice += random.randint(1,6)
    temperature_score = dice + temperature_modifier.get(upp_dict.get('atmosphere_type'))
    
    upp_dict.update({'temperature' : temperature_score})

    return upp_dict


def world_image_creation(world_array, upp_serial=None):

    # Ensure the world array is a numpy array
    if not isinstance(world_array, np.ndarray):
        raise ValueError('The provided array is not a numpy array.')

    # If an upp serial number was not provided use a standard one for "earth"
    if upp_serial == None:
        upp_serial = 'A867949-D'

    # Clean the data and sort into a dictionary 
    universal_planet_profile = upp_to_dict(upp_serial)

    # TODO: Depending on geology use different sets of colors
    geology_palette = create_color_palette(universal_planet_profile)

    # TODO: Paint a colored image
    # TODO: Depending on planet size change the radius
    # TODO: Depending on atmosphear add an outer radious representing type and density
    # blue for standard (thin, medium, dense gets different alpha gradients)
    # corrosive - green
    # tainted - brown
    # insidious - purple)
    # TODO: Add stations etc flying around the planet (Station at first but in later versions
    # add for extras such as scout, military, TAS etc
    # TODO: Implement some kind of clouds hovering above the planet



# Create a perlin array
width = 500
height = 500
detail = 3
octave = 8


if __name__ == "__main__":
    perlin2d_array = perlin.perlin2d(width, height, detail, octave)

    # Scale every point up by 255 (0-255 for white levels in an image array)
    formatted = (perlin2d_array * 255).astype('uint8')

    # Use Pillow to create an image
    img = Image.fromarray(formatted)
    img.show()