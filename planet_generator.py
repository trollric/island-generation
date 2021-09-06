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
    array_colored = np.zeros(height_array.shape + (3,), dtype=np.uint8)
    height_lower_limit = 0

    width, height = height_array.shape
    for color, height_upper_limit, _ in color_palette:
        for x in range(width):
            for y in range(height):
                if height_array[x][y] <= height_upper_limit and height_array[x][y] > height_lower_limit:
                    array_colored[x][y] = colors.get_rgb_color(color)

        height_lower_limit = height_upper_limit
    
    return array_colored


def create_color_palette(upp_dict):
    """Takes a Universal Planetary Profile dictionary and determins which
    color, height level and land type has the corresponding color. The result is returned as a list
    of touples.
    E.g. ([0,0,255], 0.4, 'Water')

    Args:
        upp_dict (dictionary): Has all the UPP information stored inside.

    Raises:
        TypeError: If the provided type is not a dictionary raise an exception

    Returns:
        list of touples: Returns a list with touples with the format
        (RGB_Data, float: height level,String: landtype)
        E.g. ([0,0,255], 0.4, 'Water')
    """
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
                    'mountain':['sienna','dark_grey','grey','dim_grey','hot_pink','medium_violet_red', 'magenta'],
                    'land':['forest_green', 'dark_green', 'olive_drab','spring_green','medium_orchid'],
                    'barren_land':['sienna', 'saddle_brown', 'dark_golden_rod'],
                    'volcano': ['red']}

    # Create different land compositions for different world types.                   
    # if frozen, cold, temperate
    desert_world = [['canyon', 'sand', 'mountain'],[0.15, 0.8, 0.2]]

    # if boiling
    desert_lava_world = [['lava', 'sand', 'mountain', 'volcano'],[0.15, 0.8, 0.15, 0.05]]

    # normal
    dry_world = [['water', 'sand', 'land', 'mountain'],[None, 0.4, 0.4, 0.2]]

    # If boiling
    dry_lava_world = [['lava', 'sand', 'land', 'mountain', 'volcano'],[None, 0.4, 0.4, 0.15, 0.05]]

    # if freezing
    dry_ice_world = [['ice', 'sand', 'land', 'mountain','snow'],[None, 0.4, 0.4, 0.15, 0.05]]

    # if not supporting life special atmosphere etc.
    barren_world = [['water', 'sand', 'barren_land', 'mountain', 'snow'],[None, 0.10, 0.60, 0.20, 0.10]]
    barren_ice_world = [['ice', 'sand', 'barren_land', 'mountain', 'snow'],[None, 0.10, 0.60, 0.20, 0.10]]
    barren_hot_world = [['water', 'sand', 'barren_land', 'mountain'],[None, 0.10, 0.60, 0.30]]
    barren_lava_world = [['lava', 'barren_land', 'mountain','volcano'],[None, 0.6, 0.35, 0.05]]

    # life supporting worlds. peaks are ice.
    garden = [['water', 'sand', 'land', 'mountain', 'snow'],[None, 0.05, 0.60, 0.30, 0.05]]
    garden_ice = [['ice', 'snow','mountain','snow'],[None, 0.65, 0.30, 0.05]]
    garden_hot = [['water', 'sand', 'land', 'mountain'],[None, 0.10, 0.55, 0.35]]
    garden_lava = [['water', 'sand', 'land', 'mountain','volcano'],[None, 0.20, 0.45, 0.30, 0.05]]

    # garden worlds when freezing. Water is ice. no sand, land is snow. mountains are rock. Peaks are ice
    ice_world = [['ice', 'snow'],[0.95, 0.05]]
    water_world = [['water'],[1.00]]
    water_lava_world = [['water', 'sand', 'mountain', 'volcano'],[0.95, 0.45, 0.50, 0.05]]


    # World array [[land_type],[percentage]] if percentage none the height will be determined from
    # hydrographic percentage
    world = [[],[]]

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
            if upp_dict.get('atmosphere_type') >= 10 and upp_dict.get('atmosphere_type') <= 12:
                world = barren_ice_world
            else:
                world = garden_ice

        elif upp_dict.get('temperature') == 'cold':
            if upp_dict.get('atmosphere_type') >= 10 and upp_dict.get('atmosphere_type') <= 12:
                world = barren_world
            else:
                world = garden

        elif upp_dict.get('temperature') == 'temperate':
            if upp_dict.get('atmosphere_type') >= 10 and upp_dict.get('atmosphere_type') <= 12:
                world = barren_world
            else:
                world = garden

        elif upp_dict.get('temperature') == 'hot':
            if upp_dict.get('atmosphere_type') >= 10 and upp_dict.get('atmosphere_type') <= 12:
                world = barren_hot_world
            else:
                world = garden_hot

        elif upp_dict.get('temperature') == 'boiling':
            if upp_dict.get('atmosphere_type') >= 10 and upp_dict.get('atmosphere_type') <= 12:
                world = barren_lava_world
            else:
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

    # Set waterlevel
    if world[1][0] == None:
        world[1][0] = upp_dict.get('hydrographic_percentage')*0.1  

    # 2. Calculate heights.
    # 2.a First remove the water level. Since the rest is calculated using percentage of the remaineder after
    # the lowest level.
    palette.append( (random.choice(land_types.get(world[0][0])),
                    world[1].pop(0),
                    world[0].pop(0)))

    # Now add the restof the elements calculated
    water_level = palette[0][1]
    height = water_level

    for land, percent in zip(world[0],world[1]):
        height += (1-water_level)*percent
        palette.append( (random.choice(land_types.get(land)),
                        height,
                        land))

    # percentages would work best. Hydrographic 3 would be 0.30 (30%).
    # The rest of the values should be a distribution of these values.
    # Example dry world may be 40% sand. If hydrograhic percentage is 3 => 0.35 the height of sand
    # Should be (1-0.35)*0.4 + previous height level. 1-0.35 = 0.65. 0.65*0.4 = 0.26. 0.35+0.26 = 0.61

    return palette


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

def to_planet_shape(world_array, upp_dict):
    """Takes a colored world array and cuts out everything outside of the desired radius. Creating a round
    planetoid shape. The radius is derived from the Universal Planetary Profile

    Args:
        world_array (np.ndarray): A numpy array with RGB color lists.
        upp_dict (dict): Dictionary containing the planet Universal Planetary Profile

    Returns:
        np.nddarray: The masked array creating the planetoid shape.
    """
    # Get width and height of the world array.
    width, height, _ = world_array.shape
    # calculate the radius of the planet to 8-88% of the smallest axis leaving 12% for atmosphere
    if width <= height:
        smallest_axis = width
    else:
        smallest_axis = height

    r = (smallest_axis/2) * (0.08*(1+upp_dict.get('size')))
    y,x = np.ogrid[-height/2:height/2, -width/2:width/2]

    # creates a mask with True False values
    # at indices
    mask = x**2+y**2 <= r**2

    black = colors.get_rgb_color('black')
    planet_world = np.zeros_like(world_array)

    for i in range(width):
        for j in range(height):
            if mask[i][j]:
                planet_world[i][j] = world_array[i][j]
            else:
                planet_world[i][j] = black
    
    return planet_world

def world_image_creation(world_array, upp_serial=None):

    # Ensure the world array is a numpy array
    if not isinstance(world_array, np.ndarray):
        raise ValueError('The provided array is not a numpy array.')

    # If an upp serial number was not provided use a standard one for "earth"
    if upp_serial == None:
        upp_serial = 'A867949-13'

    # Clean the data and sort into a dictionary 
    universal_planet_profile = upp_to_dict(upp_serial)

    # Depending on geology use different sets of colors
    geology_palette = create_color_palette(universal_planet_profile)

    # Paint a colored image
    colored_world = color_array(world_array, geology_palette)


    # TODO: Depending on planet size change the radius
    planet_world = to_planet_shape(colored_world, universal_planet_profile)

    # TODO: Depending on atmosphear add an outer radious representing type and density
    # blue for standard (thin, medium, dense gets different alpha gradients)
    # corrosive - green
    # tainted - brown
    # insidious - purple)
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
    # TODO: Add stations etc flying around the planet (Station at first but in later versions
    # add for extras such as scout, military, TAS etc
    # TODO: Implement some kind of clouds hovering above the planet
    # TODO: return the planet image.
    return planet_world 

def main():
    # Create a perlin array
    width = 300
    height = 300
    detail = 2
    octave = 8

    perlin2d_array = perlin.perlin2d(width, height, detail, octave)
    planet_array = world_image_creation(perlin2d_array)

    img = Image.fromarray(planet_array, 'RGB')
    img.show()


if __name__ == "__main__":
    main()