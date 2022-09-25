# Takes an UPP dictionary (Universal planetary profile) and cretes a map legend
# This include descriptive name of the different colors, goverment type, temperature range,
# Atmosphearic demands, Startport quality and trade codes.
import json
import os
import colors
from planet_generator import create_color_palette
from planet_generator import upp_to_dict
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



def value_in_range(value, min, max):
    """Takes a value and checks if its greater or equal to min and less or equal to max

    Args:
        value (integer/float): An integer or float value to be checked against min and max
        min (integer/float): The minimum value of the range
        max (integer/float): The maximum value of the range

    Returns:
        [Boolean]: Returns a true/false evaluation
    """
    evaluation = False

    if value >= min and value <= max:
        evaluation = True
    
    return evaluation


def determine_trade_codes(upp_dict):
    """Takes a universal planetary profile dictionary and checks wich trade codes apply to the
    planet.

    Args:
        upp_dict (Dict): A dictionary containing all the universal planetary profile information

    Raises:
        ValueError: Raises a ValueError if the number of tests passed is greater than the number
        of passable tests.

    Returns:
        List: Returns a list of tradecodes.
    """
    # Load the trade code determinants from JSON.
    with open("trade_code_classification.json",) as trade_requirement_data:
        trade_requirements = json.load(trade_requirement_data)

    categorization = []
    # Start checking wich codes apply going through each element in the json data.
    for _, type_requirements in trade_requirements.items():
        
        # Set requirement met to False
        trade_code_requirement_met = False

        # Set test variables
        number_of_tests = 0
        number_of_passed_tests = 0

        # Count number of tests to pass
        for key, requirement in type_requirements.items():
            # Code is not a test but the tradecode appended if all tests pass
            if not key == 'code' and not requirement == None:
                number_of_tests += 1

        # Perform the tests
        for key, requirement in type_requirements.items():
            if not key == 'code' and not requirement == None:
                if requirement[0] == 'range':
                    min, max = requirement[1], requirement[2]
                    if value_in_range(upp_dict.get(key), min, max):
                        number_of_passed_tests += 1
                elif requirement[0] == 'specific':
                    if upp_dict.get(key) in requirement[1]:
                        number_of_passed_tests += 1

        if number_of_passed_tests == number_of_tests:
            trade_code_requirement_met = True
        elif number_of_passed_tests > number_of_tests:
            raise ValueError('Number of passed test can not exceed the total number of tests.')
        # Append the viable trade codes to a list if all requirements are met.
        if trade_code_requirement_met:
            categorization.append(type_requirements.get('code'))

    return categorization


def generate_legend_document():
    """Creates a fillable form to enter all the generated data into.
    Aspects: A4 300DPI (3508x2480 px)

    Returns:
        Image: Returns a fillable image form.
    """
    # Values are without bleed area
    # Size Name	    Size in mm      Size in pixels 300dpi
    # A7	        105 x 74  mm	1240 x 874 px
    # A6	        148 x 105 mm	1748 x 1240 px
    # A5	        210 x 148 mm	2480 x 1748 px
    # A4	        297 x 210 mm	3508 x 2480 px

    # Create a new empty Image as a portrait A4. And draw class.
    legend_height = 3508
    legend_width = 2480
    legend_im = Image.new('RGBA', (legend_width, legend_height))
    legend_draw = ImageDraw.Draw(legend_im)

    # Chose a background fill color.
    background = tuple(colors.get_rgb_color('dim_gray'))

    # Select a line color (remember PIL uses tuples)
    line_fill_color = tuple(colors.get_rgb_color('orange_red'))
    line_width = 12

    # Draw the legnd boundary lines.
    legend_draw.rectangle([(0, 0), (legend_width, legend_height)],
                                    outline=line_fill_color,
                                    fill=background,
                                    width=line_width)
    
    # First three boxes ratio 1-1-1
    x = int(legend_width/3)
    y = x
    div1 = [(x, 0), (x, y)]
    div2 = [(x*2, 0), (x*2, y)]
    sep1 = [(0, y),(x*3, y)]
    lines = [div1, div2, sep1]
    
    # Second set of boxes ratio width ratio 2-1
    # Height ratio 1/3 + 1/4 = 7/12
    y = int(legend_width/12)
    # Divider
    lines.append([(0, y*7), (legend_width, y*7)])
    # separator at 2-1 ratio.
    lines.append([(x*2, y*4), (x*2, y*7)])

    # Thid box width 1-1 ratio
    # Height half of the box above 3/24 part of width
    x = int(legend_width/2)
    y = int(legend_width/24)
    # Divider 7/12 + 3/24 => 14/24 + 3/24 = 17/24
    lines.append([(0, y*17), (legend_width, y*17)])
    # Separator all the way down.
    lines.append([(x, y*14), (x, legend_height)])

    # Add a divider inside the trade box
    half_box_y = int(y*3/2)
    lines.append([(x, y*14 + half_box_y), (legend_width, y*14 + half_box_y)])
    # Add separator for Buy/Sell tabs.
    lines.append([(int(x*3/2), y*14 + half_box_y), (int(x*3/2), legend_height)])

    # Calculated remaining space for the contraband section and draw lines
    # evenly distributed. (Weapons, Armour, Information, Technology, Travelers, Psionics)
    # numbers 6 categories.

    y_dist = (legend_height - y*17) / 6
    y_zero = y*17

    for y in range(6):
        y_coord = y_zero + y*y_dist
        lines.append([(0, y_coord), (x, y_coord)])

    # Draw all lines 
    for line in lines:
        legend_draw.line(line, fill=line_fill_color, width=line_width)

    return legend_im


def validate_trade_codes(trade_codes):
    """Takes a list of trade_codes and checks if they are all correct trade code strings.

    Args:
        trade_codes (list): List of trade codes to be validated.

    Returns:
        bool: Returns true if all vales in the list are actual trade codes.
    """
    valid_trade_codes = ['Ag', 'As', 'Ba', 'De', 'Fl', 'Ga', 'Hi', 'Ht',
                            'Ic', 'In', 'Lo', 'Lt', 'Na', 'Ni', 'Po', 'Ri',
                            'Va', 'Wa', 'Amber', 'Red']
    result = True
    for code in trade_codes:
        if not code in valid_trade_codes:
            result = False
            break
    return result


def get_trade_goods(trade_codes):
    """Takes a list of trade codes.
    Example: ['Ni', 'Ht', 'Wa']

    Args:
        trade_codes (list): A list containing the viable trade codes of the planet.
        Eg. ['Ni', 'Ht', 'Wa']

    Raises:
        TypeError: If the provided variable is not a list raise an Error.

    Returns:
        dict: Returns a dictionary with different types of trade items with potential buy/sell dm
    """
    # Check that trade_codes is a list.
    if not isinstance(trade_codes, list):
        raise TypeError('Trade codes needs to be a list of traveler trade codes.')
    
    # Check that all values inside trade_codes are trade codes.
    if not validate_trade_codes(trade_codes):
        raise TypeError(f'One or more trade codes are not valid.\nCodes: {trade_codes}')

    # Import the json-data
    with open("trade_goods_table.json",) as trade_goods_data:
        trade_requirements = json.load(trade_goods_data)
    

    # Step through the data
    trade_goods = {}
    for type, goods_data in trade_requirements.items():

        # Step through trade codes and check if they are available, if they have buy dm, if they have sell dm.
        available = False
        purchase_dm = 0
        sell_dm = 0
        for code in trade_codes: 
            # Is the goods available at the planet.
            if code in goods_data.get('availability') or 'all' in goods_data.get('availability'):
                available = True

            # If there is a buy dm save the highest applicable.
            if not goods_data.get('purchase_dm').get(code) == None:
                if goods_data.get('purchase_dm').get(code) > sell_dm:
                    purchase_dm = goods_data.get('purchase_dm').get(code)

            # If there is a sell dm save the highest one applicable.
            if not goods_data.get('sale_dm').get(code) == None:
                if goods_data.get('sale_dm').get(code) > sell_dm:
                    sell_dm = goods_data.get('sale_dm').get(code)
        
        # If available and a buy or sell dm exist save the highest one that occured
        if available or purchase_dm > 0 or sell_dm > 0:
            trade_goods.update({type : {'purchase_dm' : purchase_dm, 'sale_dm' : sell_dm}})


    return trade_goods


def box_dimension_error():
    """Raises a verbose error if box dimensions have not been given
    in the correct way

    Raises:
        TypeError: Raises error with explanation how box dimensions needs to be provided.
    """
    raise TypeError('''The box dimensions needs to be given in on of the following forms
                            tuple: (width, height),\n
                            list of tuples: [(x1, y1), (x2, y2)],\n
                            list of coordinate values: [x1, y1, x2, y2]''')


def box_dimensions_valid(box_dimensions):

    # Check that box dimensions have been given correctly

    # If box dimensions is a list of tuples or ints
    if isinstance(box_dimensions, list):

        # If the box dimension list contains to many or to few items.
        if not len(box_dimensions) in [2, 4]:
            raise ValueError(f'List length expected 2 or 4. Received len:{len(box_dimensions)}')

        # If box dimension is of tuple type.
        elif len(box_dimensions) == 2:
            # Check that all items are tuples
            if not all(isinstance(value, tuple) for value in box_dimensions):
                raise ValueError(f'''Both list elements needs to be touples containing int values.\n
                                Ex: [(10, 10), (20, 20)].\n
                                provided types: [{type(box_dimensions[0])}, 
                                {type(box_dimensions[1])}''')

            # Also check that the tuples only contain integers
            for items in box_dimensions:
                if not all(isinstance(value, int) for value in items):
                    raise TypeError(f'All values needs to be of type int.\nProvided: {items}')

        # If box dimension is of a four int value list type.
        elif len(box_dimensions) == 4:
            if not all(isinstance(value, int) for value in box_dimensions):
                raise ValueError(f'All four x and y values needs to be of type integer')

    return True


def font_align(box_dimensions, horizontal = 'left', vertical = 'top', padding = 0):

    pass




def legend_append_trade_codes(legend_image, trade_codes):
    
    # Get image size
    legend_width, legend_height = legend_image.size
    # Create coordinate offset to upper left of the box
    x_off = int(legend_width/2)
    y_off = int(legend_width * 7/12)

    # Create imagedraw object
    legend_draw = ImageDraw.Draw(legend_image)

    # Create a font
    # Font size in pixels
    font_color = tuple(colors.get_rgb_color('gold'))
    font_size = int(legend_height/60)
    font = ImageFont.truetype("Fonts/Optima-LT-Medium-Italic.ttf", font_size)
    padding = 20

    # Write Trade Codes: <And add every trade code
    trade_string = ', '.join(trade_codes)
    text = f'Trade codes: {trade_string}'
    text_coord = (x_off + padding, y_off + padding)
    legend_draw.text(text_coord, text, font_color, font=font)

    # Add text purchase info and sell info.
    text = 'Trade goods'
    x, y = font.getsize(text)
    text_x_alignment = int((legend_width/4 - x)/2)
    text_y_alignment = int((legend_width * 3/48 - y)/2)
    text_coord = (x_off + text_x_alignment , y_off + text_y_alignment + (legend_width * 3/48))
    legend_draw.text(text_coord, text, font_color, font=font)

    text = 'Purchase DM | Sell DM'
    x, y = font.getsize(text)
    text_coord = (x_off + legend_width/4 +text_x_alignment , y_off + text_y_alignment + (legend_width * 3/48))
    legend_draw.text(text_coord, text, font_color, font=font)

    # Get which types of trade goods should be appended.
    eligible_trade_goods = get_trade_goods(trade_codes)

    # TODO: Append trade codes in the bottom right.



    return legend_image


def generate_legend(upp_dict, color_palette, path, planet_name):
    """Generates a planetary legend to give better overview for players.

    Args:
        upp_dict (dict): an UPP dictionary containing all generated planetary aspects.
        color_palette (dict): A dictionary containing the colors and color names used in painting the world (E.g. grass : "turtle_green")
        path (str): string providing the folder where the planetary image has been saved.
        planet_name (str): name of the planet. Used to ensure the legends name will be <planet name>_legend
    """
    # Make sure the path directory exist. Otherwise create it.
    if not os.path.exists(path):
        os.makedirs(path)

    # Generate legend layout document as an Image.
    legend_doc = generate_legend_document()

    # Determine trade codes and add to legend document.
    trade_codes = determine_trade_codes(upp_dict)

    # TODO: Append trade information to bottom right of the legend document.
    legend_doc = legend_append_trade_codes(legend_doc, trade_codes)

    # TODO: Append gravity and diamater data to the top middle of the legend document

    # TODO: Append planetary image to the top right of the legend document
    
    # TODO: Append a color to landmass type underneath the planetary image.

    # TODO: Append planet name, UPP-Serial to the top left of the legend document.

    # TODO: Determine government type, generate factions and add cultures.
    # TODO: Append the data underneath around temperature data.

    # TODO: Generate a random day/night cycle with a temperature graph (maybe using matplotlib)
    # append atmo type and necessary protections, temperature min/max daycycle data
    # to the left of the graph.

    # TODO: Determine contraband and append them to the bottom left under separate categories.

    legend_doc.show()
    # Create path to save location
    planet_name += '_legend'
    path = os.path.join(path, planet_name)

    # TODO: Save image to path with <name>_legend.


def main():
    # If called directly. Make planetary data up.
    upp_dict = upp_to_dict('A344556-10')
    color_palette = create_color_palette(upp_dict)
    path = os.path.join(os.getcwd(), 'Saved')
    planet_name = 'Debug'

    generate_legend(upp_dict, color_palette, path, planet_name)


if __name__ == '__main__':
    main()