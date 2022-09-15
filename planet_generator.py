# Generates a planet using perlin noise and a
# serial string from the Traveler 2nd edition
import imp
from math import sqrt
from turtle import width
import perlin2d as perlin
import numpy as np
import random
import colors
import converter
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import os



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
    array_colored = np.zeros(height_array.shape + (4,), dtype=np.uint8)
    height_lower_limit = 0

    width, height = height_array.shape
    for color, height_upper_limit, _ in color_palette:
        for x in range(width):
            for y in range(height):
                if height_array[x][y] <= height_upper_limit and height_array[x][y] > height_lower_limit:
                    array_colored[x][y] = colors.get_rgb_color(color, 255)

        height_lower_limit = height_upper_limit
    
    return array_colored


def create_color_palette(upp_dict):
    """Takes a Universal Planetary Profile dictionary and determins which
    color, height level and land type has the corresponding color. The result is returned as a list
    of touples.
    E.g. ('blue', 0.4, 'Water')

    Args:
        upp_dict (dictionary): Has all the UPP information stored inside.

    Raises:
        TypeError: If the provided type is not a dictionary raise an exception

    Returns:
        list of touples: Returns a list with touples with the format
        (RGB_Data, float: height level,String: landtype)
        E.g. ('blue, 0.4, 'Water')
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
        TypeError: If the provided upp_string is not of type string.
        ValueError: If any individual UPP value is outside of bounds.

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
    
    # If spaceport quality = X (Set it to 0)
    upp_string = upp_string.replace('X', '0')

    upp_dict = {}
    for variable_name, upp_value in zip(upp_variables, upp_string):
        upp_dict.update({variable_name : int(upp_value, 16)})

    # Check if any UPP value is outside of bounds.

    # Starport quality [0 (for X-none) or A-E]
    if (upp_dict['starport_quality'] > 0 and upp_dict['starport_quality'] < 10) or upp_dict['starport_quality'] > 14:
        starport_value = upp_dict['starport_quality']
        raise ValueError(f'Starport quality must be of values 0(sybol for X) or between A-E \n Starport value provided: {starport_value}')

    # Size [1-A]
    if upp_dict['size'] < 1 or upp_dict['size'] > 10:
        size_value = upp_dict['size']
        raise ValueError(f'Planet size needs to be between 1-A in size. \n Size value provided: {size_value}')

    # Atmosphere type [0-F]
    if upp_dict['atmosphere_type'] < 0 or upp_dict['atmosphere_type'] > 15:
        atmo_value = upp_dict['atmosphere_type']
        raise ValueError(f'Atmosphere types can only range between 0-F \n Atmosphere value entered: {atmo_value}')

    # Hydrographic percentage [0-A]
    if upp_dict['hydrographic_percentage'] < 0 or upp_dict['hydrographic_percentage'] > 15:
        hydro_value = upp_dict['hydrographic_percentage']
        raise ValueError(f'Hydrographic percentage must range beetween 0-A. \n Hydrographic value provided: {hydro_value}')

    # Population [0-C]
    if upp_dict['population'] < 0 or upp_dict['population'] > 12:
        pop_value = upp_dict['population']
        raise ValueError(f'Population must range beetween 0-C. \n Population value provided: {pop_value}')

    # Goverment type [0-F]
    if upp_dict['government_type'] < 0 or upp_dict['government_type'] > 15:
        gov_value = upp_dict['government_type']
        raise ValueError(f'Goverment type must range beetween 0-A. \n Goverment type value provided: {gov_value}')

    # Law level [0-F]
    if upp_dict['law_level'] < 0 or upp_dict['law_level'] > 15:
        law_value = upp_dict['law_level']
        raise ValueError(f'Law level must range beetween 0-A. \n Law level value provided: {law_value}')

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

    Raises:
        TypeError: If the array is not an numpy array the alrogitm fails.
        TypeError: If the the universal planetary profile is not converted to a dictionary
        size can not be gathered.

    Returns:
        np.nddarray: The masked array creating the planetoid shape.
    """
    if not isinstance(world_array, np.ndarray):
        raise TypeError('World array needs to be a numpty ndarray for the algoritm to work')
    
    if not isinstance(upp_dict, dict):
        raise TypeError('upp_dict needs to be cleaned from string to dictionary format')
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

    black = colors.get_rgb_color('black', 0)
    planet_world = np.zeros_like(world_array)

    for i in range(width):
        for j in range(height):
            if mask[i][j]:
                planet_world[i][j] = world_array[i][j]
            else:
                planet_world[i][j] = black
    
    return planet_world


def add_atmosphere(planet_world, upp_dict):
    """Paints an atmosphere around the planetary array depecting what type and density of the
    planetary atmosphere

    Args:
        planet_world (np.ndarray): A colored RGB array converted to a planetary shape
        upp_dict (dict): Dictionary containing the planets universal planetary profile

    Raises:
        TypeError: If the array is not an numpy array the alrogitm fails.
        TypeError: If the the universal planetary profile is not converted to a dictionary
        size can not be gathered.

    Returns:
        np.ndarray: Numpy array containing the colored planet with an added atmoshperic layer.
    """

    if not isinstance(planet_world, np.ndarray):
        raise TypeError('The planetary array needs to be an numpy array')

    if not isinstance(upp_dict, dict):
        raise TypeError('The Universal planetary profile needs to be converted to a dictionary')
    # Fetch the atmosphere color
    density = 255
    fall_off = 1

    if upp_dict.get('atmosphere_type') == 0:
        # No atmosphere
        color = 'black'
        density *= 0
    elif upp_dict.get('atmosphere_type') == 1:
        # Trace
        color = 'sky_blue'
        density *= 0.25
    elif upp_dict.get('atmosphere_type') == 2:
        # Very thin and tainted
        color = 'chocolate'
        density *= 0.5
    elif upp_dict.get('atmosphere_type') == 3:
        # Very thin
        color = 'sky_blue'
        density *= 0.5
    elif upp_dict.get('atmosphere_type') == 4:
        # Thin and tainted
        color = 'chocolate'
        density *= 0.75
    elif upp_dict.get('atmosphere_type') == 5:
        # Thin
        color = 'sky_blue'
        density *= 0.75
    elif upp_dict.get('atmosphere_type') == 6:
        # Standard
        color = 'sky_blue'
    elif upp_dict.get('atmosphere_type') == 7:
        # Standard tainted
        color = 'chocolate'
    elif upp_dict.get('atmosphere_type') == 8:
        # Dense
        color = 'sky_blue'
        fall_off = 1.5
    elif upp_dict.get('atmosphere_type') == 9:
        # Dense tainted
        color = 'chocolate'
        fall_off = 1.5
    elif upp_dict.get('atmosphere_type') == 10:
        # Exotic
        color = 'dark_violet'
    elif upp_dict.get('atmosphere_type') == 11:
        # Corrosive
        color = 'lawn_green'
    elif upp_dict.get('atmosphere_type') == 12:
        # Insidious
        color = 'yellow'
    elif upp_dict.get('atmosphere_type') == 13:
        # Very dense
        color = 'sky_blue'
        fall_off = 2
    elif upp_dict.get('atmosphere_type') == 14:
        # low
        color = 'sky_blue'
        density *= 0.6
    elif upp_dict.get('atmosphere_type') == 15:
        # Unusual
        color = 'pale_green'


    # Get width and height of the world array.
    width, height, _ = planet_world.shape

    # calculate the radius of the planet to 8-88% of the smallest axis leaving 12% for atmosphere
    if width <= height:
        smallest_axis = width
    else:
        smallest_axis = height

    r = (smallest_axis/2) * (0.08*(1+upp_dict.get('size')))
    atmosphere_range = (smallest_axis/2) * 0.12
    centre_x, centre_y = width/2, height/2
    # add colors here
    for x in range(width):
        for y in range(height):
            delta_x = x-centre_x
            delta_y = y-centre_y
            dist = sqrt(delta_x**2+delta_y**2)

            if dist-r >= 0 and dist-r < atmosphere_range:
                alpha = int(density*(1-((dist-r)/atmosphere_range)/fall_off))
                planet_world[x][y] = colors.get_rgb_color(color, alpha)
    
    return planet_world

def add_station(planet_world, upp_dict):
    # if station quality is not none or 0.
    if not upp_dict['starport_quality'] == 0 and not upp_dict['starport_quality'] == None:
        # read in space station stock file.
        station_image = Image.open('Images/space-station.png')

        # If no planet world is provided. Create a blank numpy array.
        if not isinstance(planet_world, np.ndarray):
            planet_width, planet_height = 500,500
            planet_world = np.empty((planet_width, planet_height, 4))
        else:
            planet_width, planet_height, _ = planet_world.shape

        # Resize to 5% of the width and height values of planet_world.
        station_width = int(0.1 * planet_width)
        station_height = int(0.1 * planet_height)
        station_image = station_image.resize((station_width, station_height))

        # add a letter to the station.
        letter_color = colors.get_rgb_color('red')
        # Font size in pixels
        font_size = int(station_height/2)
        font = ImageFont.truetype("Fonts/Optima-LT-Medium-Italic.ttf", font_size)
        draw_on_station = ImageDraw.Draw(station_image)

        # Decice what letter to stamp the station with.
        letter = ""
        if upp_dict['starport_quality'] == 10:
            letter = "A"
        elif upp_dict['starport_quality'] == 11:
            letter = "B"
        elif upp_dict['starport_quality'] == 12:
            letter = "C"
        elif upp_dict['starport_quality'] == 13:
            letter = "D"
        elif upp_dict['starport_quality'] == 14:
            letter = "E"

        # Get font size and position the letter in the center.
        x, y = font.getsize(letter)
        x = int((station_width-x)/2)-1
        y = int((station_height-y)/2)-1
        
        draw_on_station.text((x, y), letter, tuple(letter_color), font=font)

        # convert to a np_array.
        im_as_array = np.asarray(station_image)

        # replace the values of the array in the top left corner
        im_width, im_height, _ = im_as_array.shape
        for x in range(im_width):
            for y in range(im_height):
                planet_world[x][y] = im_as_array[x][y]

    return planet_world

def world_image_creation(world_array, upp_serial=None):
    """Takes a 2d perlin noise array cleaned to values ranging 0-1

    Args:
        world_array (np.ndarray): numpy array containing the perlin noise data.
        upp_serial (string, optional): The universal planetar profile string.. Defaults to None.

    Raises:
        TypeError: The perlin noise array needs to be an numpy array to work properly.
        TypeError: Uiversal planetary profile needs to follow the convention fron the Traveler 2e rulebook

    Returns:
        [type]: [description]
    """
    # Ensure the world array is a numpy array
    if not isinstance(world_array, np.ndarray):
        raise TypeError('The provided array is not a numpy array.')

    # If an upp serial number was not provided use a standard one for "earth"
    if upp_serial == None:
        upp_serial = 'A867949-13'

    if not upp_serial == None:
        if not isinstance(upp_serial, str):
            raise TypeError('''Planetary profile needs to be a string of hexadecimal numbers ending on a
            hyphen followed by a double digit decimal number. Ex. A867949-12''')


    # Clean the data and sort into a dictionary 
    universal_planet_profile = upp_to_dict(upp_serial)

    # Depending on geology use different sets of colors
    geology_palette = create_color_palette(universal_planet_profile)

    # Paint a colored image
    colored_world = color_array(world_array, geology_palette)

    # Depending on planet size change the radius
    planet_world = to_planet_shape(colored_world, universal_planet_profile)

    # Depending on atmosphear add an outer radious representing type and density
    planet_world_with_atmosphere = add_atmosphere(planet_world, universal_planet_profile)

    # Add stations etc flying around the planet (Updates could include TAS, Scout Etc)
    planet_world_with_station = add_station(planet_world_with_atmosphere, universal_planet_profile)

    # TODO: Implement some kind of clouds hovering above the planet
    # Return the planet image.

    # TODO: Implement cities etc based on population.

    return planet_world_with_station 


def validate_universal_planetary_profile(upp_string):
    """Takes an user provided universal planetary profile and validates it.

    Args:
        upp_string (string): String containing universal planetary profile

    Raises:
        ValueError: The UPP string needs to be of length 9 or 10
        ValueError: The UPP string needs to separate tech level with an hyphen
        ValueError: The UPP string needs to be seven hexadecimal numbers followed by an hyphen
        ValueError: The Upp string needs to have an integer between 0-99 after the hyphen.

    Returns:
        bool: Returns true if the UPP_String passes all the validation tests.
    """
    # Check that string length is 9 or 10 long

    if not (len(upp_string) >= 9 and len(upp_string) <= 10):
        raise ValueError(f"An UPP string is between 9 or 10 characters long. The string provided was {len(upp_string)} long.") 
    elif not (upp_string[-2] == '-' or upp_string[-3] == '-'):
        # Check that the UPP-string contains the necessary hyphen.
        raise ValueError(f'Tech level needs to be an integer between 0-99 separated by a "-" hyphen.')

    check_hexadecimal, check_integer = upp_string.split('-')
    if not len(check_hexadecimal) == 7:
        raise ValueError('The UPP needs to be seven hexadecimal numbers followed by a hyphen.')
    
    if not len(check_integer) > 0 and len(check_integer) <= 2:
        raise ValueError('The UPP string must contain an integer of 0-99 at the end after the hyphen.')
    
    # Check that every number up until the hyphen is a hexadecimal.
    # Check that technology level is entered as integer
    
    int(check_hexadecimal, 16)
    int(check_integer)

    return True


def print_help():
    """Prints the help message"""
    print("""An UPP string is described with 7 hexadecimal numbers followed by a hyphen and tech level as an integer. E.g. A867949-13\n
    UPP Value order (Starport quality, Size, Atmosphere type, Hydrographic percentage, Population, Goverment type, Law level, Tech level)\n
q, quit or exit command can be given to terminate the program.\n
h or help can be entered to get this information provided again.""")


def main(DEBUG_MODE = False):
    # Create a perlin array
    width = 500
    height = 500
    detail = 1
    octave = 8

    #perlin2d_array = perlin.perlin2d(width, height, detail, octave)
    #planet_array = world_image_creation(perlin2d_array)

    #img = Image.fromarray(planet_array, 'RGBA')
    #img.show()
    # While loop
    if not DEBUG_MODE:
        print("""Please provide a universal planetary profile.""")
    else:
        # Add debug calls and codes here.
        add_station(None, upp_to_dict('AA86AAA-10'))

    while True and not DEBUG_MODE:
        # Take user input
        user_command = input("Command: ")
        # Ensure input is lowercase
        user_command.lower()

        # Follow the user provided command or generate using universal planetary profile
        if user_command == "h" or user_command == "help":
            # print the help text.
            print_help()
        elif user_command == "q" or user_command == "quit" or user_command == "exit":
            # Exit the loop which terminates the program.
            break
        else:
            try:
                validate_universal_planetary_profile(user_command)
                # Generate a perlin noise array and use it create a planet
                perlin_planet = perlin.perlin2d(width, height, detail, octave)
                planet_array = world_image_creation(perlin_planet, user_command)
                
                # Generate an image from the colored array and preview it to the user.
                planet_image = Image.fromarray(planet_array, 'RGBA')
                planet_image.show()

                # Ask if user wants to keep the image.
                user_input = input("Would you like to keep this planet? Y/n: ")
                user_input.lower()
                # Keep asking until the user provides correct input.
                while user_input not in ['y', 'n', '', 'yes', 'no']:
                    user_input = input("You must enter [Y]es or [n]o")
                    user_input.lower()
                
                if user_input in ['yes', 'y', '']:
                    # Collect planet name from user for saving purposes.
                    planet_name = input("What is the planet called?\n")
                    path = os.path.join(os.getcwd(), 'Saved')

                    # Make sure the save directory exist. Otherwise create it.
                    if not os.path.exists(path):
                        os.makedirs(path)

                    # Save the file at the saved directory with user provided name as PNG.
                    path = os.path.join(path, planet_name)
                    planet_image.save(path, 'PNG')
            except ValueError as err:
                print('An error occured.')
                print(err)
                print_help()
                

    # TODO: Create a Legend for the planet.


if __name__ == "__main__":
    debug = False
    main(debug)