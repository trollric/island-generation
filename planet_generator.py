# Generates a planet using perlin noise and a
# serial string from the Traveler 2nd edition
import perlin2d as perlin
import numpy as np
import random
import colors
from PIL import Image



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
    
    # Palette is a list containing touples with color, height_level, legend name information.
    # Ex. ('dark_magenta', 0.4, 'canyon')
    palette = []

    # Different colors for different land types. 
    land_types = {  'lava':['red'],
                    'ice':['aqua','aqua_marine'],
                    'water':['navy','dark_blue'],
                    'canyon':['purple', 'dark_magenta','dark_slate_gray','maroon'],
                    'sand': ['crimson', 'salmon', 'tomato','sandy_brown', 'peach_puff','violet', 'orchid','plum'],
                    'snow':['snow', 'ivory', 'ghost_white'],
                    'mountain':['scienna','dark_grey','grey','dim_grey','hot_pink','medium_violet_red', 'magenta'],
                    'land':['forest_green', 'dark_green', 'olive_drab','spring_green','medium_orchid'],
                    'barren_land':['scienna', 'saddle_brown', 'dark_golden_rod'],
                    'volcano': ['red']}

    # Create different land compositions for different world types.                   
    # if frozen, cold, temperate
    desert_world = ['canyon', 'sand', 'mountain']

    # if boiling
    desert_lava_world = ['lava', 'sand', 'mountain', 'volcano']

    # normal
    dry_world = ['water', 'sand', 'land', 'mountain']

    # If boiling
    dry_lava_world = ['lava', 'sand', 'land', 'mountain', 'volcano']

    # if freezing
    dry_ice_world = ['ice', 'sand', 'land', 'mountain','snow']

    # if not supporting life special atmosphere etc.
    barren_world = ['water', 'sand', 'barren_land', 'mountain', 'snow']

    # if freezing
    barren_ice_world = ['ice', 'sand', 'barren_land', 'mountain', 'snow']

    # if boiling
    barren_lava_world = ['canyon', 'barren_land', 'mountain','volcano']

    # life supporting worlds. peaks are ice.
    garden = ['water', 'sand', 'land', 'mountain', 'snow']
    garden_ice = ['ice', 'snow','mountain','snow']
    garden_hot = ['water', 'sand', 'land', 'mountain']
    garden_lava = ['water', 'sand', 'land', 'mountain','volcano']

    # garden worlds when freezing. Water is ice. no sand, land is snow. mountains are rock. Peaks are ice
    ice_world = ['ice', 'snow']
    water_world = ['water']
    water_lava_world = ['water', 'sand', 'mountain', 'volcano']


    # The array to be creted from
    world = []

    if upp_dict.get('hydrographic_percentage') == 0:
        if upp_dict.get('temperature') == 'boiling':
            world = desert_lava_world

        else:
            world = desert_world

    elif upp_dict.get('hydrographic_percentage') >= 1 and upp_dict.get('hydrographic_percentage') < 4:
        if upp_dict.get('temperature') == 'frozen':
            world = dry_ice_world

        elif upp_dict.get('temperature') == 'cold':
            world = dry_ice_world

        elif upp_dict.get('temperature') == 'temperate':
            world = dry_world

        elif upp_dict.get('temperature') == 'hot':
            world = dry_world

        elif upp_dict.get('temperature') == 'boiling':
            world = dry_lava_world

    elif upp_dict.get('hydrographic_percentage') >= 4 and upp_dict.get('hydrographic_percentage') < 10:
        if upp_dict.get('temperature') == 'frozen':
            world = garden_ice

        elif upp_dict.get('temperature') == 'cold':
            world = garden

        elif upp_dict.get('temperature') == 'temperate':
            world = garden

        elif upp_dict.get('temperature') == 'hot':
            world = garden_hot

        elif upp_dict.get('temperature') == 'boiling':
            world = garden_lava

    elif upp_dict.get('hydrographic_percentage') == 10:
        if upp_dict.get('temperature') == 'frozen':
            world = ice_world
        elif upp_dict.get('temperature') == 'cold':
            world = ice_world
        elif upp_dict.get('temperature') == 'temperate':
            world = water_world
        elif upp_dict.get('temperature') == 'hot':
            world = water_world
        elif upp_dict.get('temperature') == 'boiling':
            world = water_lava_world

    
    # 2. Calculate heights.
    # percentages would work best. Hydrographic 3 would be 0.35 (35%).
    # The rest of the values should be a distribution of these values.
    # Example dry world may be 40% sand. If hydrograhic percentage is 3 => 0.35 the height of sand
    # Should be (1-0.35)*0.4 + previous height level. 1-0.35 = 0.65. 0.65*0.4 = 0.26. 0.35+0.26 = 0.61

    # 3. Determine color of atmosphere
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
    Temperature frozen, cold, temperate, hot, boiling
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
    
    # Since Tech level is not hexadecimal. Split the array and handle tech level separately.
    upp_string, tech_level = upp_string.split('-')

    # Create a ditionary with name and int value pairs.
    upp_variables = [   'starport_quality',
                        'size',
                        'atmosphere_type',
                        'hydrographic_percentage',
                        'population',
                        'government_type',
                        'law_level']
    
    upp_dict = {}
    for variable_name, upp_value in zip(upp_variables, upp_string):
        upp_dict.update({variable_name : int(upp_value, 16)})

    # Handle tech level seperately
    upp_dict.update({'tech_level': int(tech_level)})
    
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
    
    if temperature_score <=2:
        upp_dict.update({'temperature':'frozen'})
    elif temperature_score <=4:
        upp_dict.update({'temperature':'cold'})
    elif temperature_score <=9:
        upp_dict.update({'temperature':'temperate'})
    elif temperature_score <=11:
        upp_dict.update({'temperature':'hot'})
    elif temperature_score >=12:
        upp_dict.update({'temperature':'boiling'})

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
    # TODO: return the planet image.

def main():
    # Create a perlin array
    width = 500
    height = 500
    detail = 3
    octave = 8

    perlin2d_array = perlin.perlin2d(width, height, detail, octave)

    # Scale every point up by 255 (0-255 for white levels in an image array)
    formatted = (perlin2d_array * 255).astype('uint8')

    # Use Pillow to create an image
    img = Image.fromarray(formatted)
    img.show()


if __name__ == "__main__":
    main()