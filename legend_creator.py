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


def validate_box_dimensions(box_dimensions):
    """Checks that box dimensions have been given properly

    Args:
        box_dimensions (tuple, list): The box_dimensions are checked to see if they are of acceptable
        types:
        tuple: (int, int): (width, height)
        list(tuple, tuple): [(int x1, int y1),(int x2, int y2)]
        list(int, int, int, int): [x1, y1, x2, y2]

    Raises:
        TypeError: box dimensions needs to be of type list or tuple
        ValueError: List length needs to be 2 or 4
        TypeError: One or more of the list elements are not of tuple type.
        TypeError: All values inside the tuples must be of int type.
        ValueError: If any int is of negative type
        ValueError: x1 can't be larger than x2, y1 can't be larger than y2
        TypeError: All values needs to be of int type.
        ValueError: If any int is negative.
        ValueError: x1 can't be larger than x2, y1 can't be larger than y2
        ValueError: Tuple not of size 2
        TypeError: Tuple values not of type int
        ValueError: One or more int values negative.
    """
    # Check that box dimensions have been given correctly

    if not isinstance(box_dimensions, (list, tuple)):
        raise TypeError('Box dimenions needs to be of type list or tuple')

    # If box dimensions is a list of tuples or ints
    if isinstance(box_dimensions, list):

        # If the box dimension list contains to many or to few items.
        if not len(box_dimensions) in [2, 4]:
            raise ValueError(f'List length expected 2 or 4. Received len:{len(box_dimensions)}')

        # If box dimension is of tuple type.
        elif len(box_dimensions) == 2:
            # Check that all items are tuples
            if not all(isinstance(value, tuple) for value in box_dimensions):
                raise TypeError(f'''Both list elements needs to be touples containing int values.\n
                                Ex: [(10, 10), (20, 20)].\n
                                provided types: [{type(box_dimensions[0])}, 
                                {type(box_dimensions[1])}''')

            # Also check that the tuples only contain integers
            for items in box_dimensions:
                if not all(isinstance(value, int) for value in items):
                    raise TypeError(f'All values needs to be of type int.\nProvided: {items}')
                
                # Check that no value in the tuple is negative.
                if not all(val >= 0 for val in items):
                    raise ValueError('All numbers needs to be of positive integer type')
            
            # Check that x1 > x2 or y1 > y2
            x1, y1 = box_dimensions[0]
            x2, y2 = box_dimensions[1]
            if x1 > x2 or y1 > y2:
                raise ValueError(f'''The secon dimension can not be smaller than the first.\n
                                provided values x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}''')

        # If box dimension is of a four int value list type.
        elif len(box_dimensions) == 4:
            if not all(isinstance(value, int) for value in box_dimensions):
                raise TypeError(f'All four x and y values needs to be of type integer')

            # Check that x2 is largen than x1 and y2 is larger than y1 and no value is smaller
            # than 0
            x1, y1, x2, y2 = box_dimensions

            if not all(val >= 0 for val in box_dimensions):
                raise ValueError('All numbers needs to be of positive integer type.')
            if x1 > x2 or y1 > y2:
                raise ValueError(f'''The second dimension can not be smaller than the first.\n
                                provided values x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}''')

        if isinstance(box_dimensions, tuple):
            if not len(box_dimensions) == 2:
                raise ValueError('tuple can only contain two values.')
            if not all(isinstance(val, int) for val in box_dimensions):
                raise TypeError('The provided values inside the tuple must be of type int.')
            if not all(val >= 0 for val in box_dimensions):
                raise ValueError('The integer values must be positive.')


def get_box_dimension_size(box_dimensions):
    """Takes a box_dimension and returns width, height as a tuple.

    Args:
        box_dimensions (tuple/list): A list of values or tuples spanning the bounding box.
        Or a tuple containing width and height.

    Returns:
        tuple: (width : int, height : int)
    """
    # Get width, heigth from box_dimensions.
    width = 0
    height = 0
    if isinstance(box_dimensions, tuple):
        width, height = box_dimensions
    elif len(box_dimensions) == 2:
        width = box_dimensions[1][0] - box_dimensions[0][0]
        height = box_dimensions[1][1] - box_dimensions[0][1]
    elif len(box_dimensions) == 4:
        width = box_dimensions[0] - box_dimensions[2]
        height = box_dimensions[1] - box_dimensions[3]
    return width,height


def get_font_align_offsets(box_dimensions, text, font, horizontal = 'left',
            vertical = 'top', padding = 0, padding_mode_percentage = False):
    """Takes a bounding box, a text and a font. With additional parameters
    as needed and returns a touple with x, y offset values to align the
    text after the provided alignment demands.

    Args:
        box_dimensions (list/tuple): A list containing two tuples or four int values. or a
        tuple containing width, height
        text (str): A text string that needs to be aligned inside a bounding box.
        font (PIL.ImageFont.FreeTypeFont): A font object that will be used to render the text.
        horizontal (str, optional): Alignment option left, center or right. Defaults to 'left'.
        vertical (str, optional): Alignment option top, center or bottom. Defaults to 'top'.
        padding (int, optional): Adds padding to the offset values. Or gives a percent value
        if padding should be dependent on the bounding box. Defaults to 0.
        padding_mode_percentage (bool, optional): If padding should be depending on the
        bounding box set to True. Defaults to False.

    Raises:
        TypeError: Text needs to be string.
        TypeError: Font needs to be a FreeTypeFont format.
        ValueError: Horizontal needs to be a string of left, center or right
        ValueError: Vertical needs to be a string of top, center or bottom.
        TypeError: Padding value must be an integer.
        ValueError: If padding is applied like percent it must be 0-100
        ValueError: If padding not based of percent it needs to be a positive integer.

    Returns:
        tuple: Returns a touple containing the alignment values for x and y inside the bounding
        box
    """
    # Check that box dimensions are valid.
    validate_box_dimensions(box_dimensions)

    # Check that text is valid.
    if not isinstance(text, str):
        raise TypeError('Text needs to be provided as a string.')

    # Check that font is of FreeTypeFont type.
    if not isinstance(font, ImageFont.FreeTypeFont):
        raise TypeError('Font needs to be of PIL.ImageFont.FreeTypeFont class.')
    
    # Check that alignment values are of correct types
    if not horizontal.lower() in ['left', 'center', 'right']:
        raise ValueError('Horizontal alignment can only be left, center or right')

    if not vertical.lower() in ['top', 'center', 'bottom']:
        raise ValueError('Vertical alignment can only be top, center or bottom')

    # Check that input padding value is valid
    if not isinstance(padding, int):
        raise TypeError('Padding needs to be provided as an int value.')

    if padding_mode_percentage and not value_in_range(padding, 0, 100):
        raise ValueError('''When providing padding in percentage it needs to be provided
         as an integer between 0-100''')
    elif not padding_mode_percentage and padding < 0:
        raise ValueError('Padding needs to be a positive integer value')


    width, height = get_box_dimension_size(box_dimensions)

    # Get text width and height with the current font
    text_width, text_height = font.getsize(text)

    # Calculate adjustment_x and adjustment_y depending on alignment settings
    # and padding options.
    adjustment_x, adjustment_y = (0, 0)
    
    # Calculate padding if needed.
    if padding_mode_percentage:
        padding = (int(width * padding/100), int(height * padding/100))
    else:
        padding = (padding, padding)
    
    # Calculate adjustment_x
    if horizontal.lower() == 'left':
        adjustment_x = padding[0]
    elif horizontal.lower() == 'center':
        adjustment_x = int((width - text_width) / 2)
    elif horizontal.lower() == 'right':
        adjustment_x = width - (text_width + padding[0])

    # Calculated adjustment_y
    if vertical.lower() == 'top':
        adjustment_y = padding[1]
    elif vertical.lower() == 'center':
        adjustment_y = int((height - text_height) / 2)
    elif vertical.lower() == 'bottom':
        adjustment_y = height - (text_height + padding[1])

    return adjustment_x, adjustment_y


def get_max_font_size(box_dimensions, text, font_path, padding = 0):
    """Takes a bouning box and returns the largest possible font size. If you wish to 
    write out text in the font from the provided font_path. Optionally space for padding
    can be taken into consideration.

    Args:
        box_dimensions (tuple/list): list of tuples or integers spanning a bounding box.
        Optionally a tuple containing width/heigh can be given.
        text (str): The text that font size will be tested with.
        font_path (str): A string containing the path to a truefont.
        padding (int, optional): Padding in the bounded box. Defaults to 0.

    Raises:
        TypeError: text needs to be a string.
        TypeError: the path must be provided as a string.
        FileNotFoundError: if the font can not be found at given path.
        TypeError: padding must be an integer.
        ValueError: padding must be a positive integer.

    Returns:
        int: Returns the largest font size that can be used for a bounded box with padding optional
        as an integer.
    """
    # Check if box_dimensions are valid
    validate_box_dimensions(box_dimensions)

    # validate text
    if not isinstance(text, str):
        raise TypeError(f'text needs to be of type string. Provided type was: {type(text)}')

    # Validate font
    if not isinstance(font_path, str):
        raise TypeError(f'font needs ot be a string. Provided type was: {type(font_path)}')
    elif not os.path.exists(font_path):
        raise FileNotFoundError(f'Could not find the font at the given path. path given: {font_path}')

    # Check padding is int and not a negative number.
    if not isinstance(padding, int):
        raise TypeError(f'padding was not an int. Type provided: {type(padding)}')
    elif not padding > 0:
        raise ValueError(f'padding must be a positive integer. Provided value: {padding}')

    # Try every font size from 1-400 until text_width or text_height is larger than the bounding box.
    font_size = 1
    width, height = get_box_dimension_size(box_dimensions)
    for size in range(1, 401):
        font = ImageFont.truetype(font_path, size)
        text_width, text_height = font.getsize(text)

        # Break if we have reached the largest font size possible.
        if text_width > width - 2 * padding or text_height > height - 2 * padding:
            break

        font_size = size

    return font_size


def legend_append_trade_codes(legend_image, trade_codes):
    
    #-------------------------
    #b1                      |
    #-------------------------
    #b2          |b3         |
    #-------------------------
    #b4          |b5         |
    #            |           |
    #            |           |
    #            |           |
    #            |           |
    #            |           |
    #            |           |
    #            |           |
    #-------------------------

    # Get image size
    legend_width, legend_height = legend_image.size

    # Create coordinate offset to upper left of b1
    x_offset = int(legend_width/2)
    y_offset = int(legend_width * 7/12)

    # Create helper veriables defining box sizes.
    half_box_y = int(legend_width * 3/48)
    box_x = int(legend_width / 2)
    half_box_x = int(legend_width / 4)

    # Create bounded boxes b1 through b5
    b1 = [(x_offset, y_offset),(x_offset + box_x, y_offset + half_box_y)]

    # Change y_offset for the next set of boxes.
    y_offset += half_box_y
    b2 = [(x_offset, y_offset), (x_offset + half_box_x, y_offset + half_box_y)]
    b3 = [(x_offset + half_box_x, y_offset), (x_offset + box_x, y_offset + half_box_y)]

    # Change y_offset for the next set of boxes
    y_offset += half_box_y
    b4 = [(x_offset, y_offset), (x_offset + half_box_x, legend_height)]
    b5 = [(x_offset + half_box_x, y_offset), (x_offset + box_x, y_offset + half_box_y)]

    # Create imagedraw object
    legend_draw = ImageDraw.Draw(legend_image)


    # Set default font values.
    font_color = tuple(colors.get_rgb_color('gold'))
    font_path = "Fonts/Optima-LT-Medium-Italic.ttf"
    padding = 20

    # Create a font for the trade_string
    trade_string = ', '.join(trade_codes)
    text = f'Trade codes: {trade_string}'
    
    # Determine maxiumum font size with padding.
    font_size = get_max_font_size(b1, text, font_path, padding)
    font = ImageFont.truetype(font_path, font_size)

    x_alignment, y_alignment = get_font_align_offsets(  b1, text, font,
                                                        vertical='center',
                                                        padding=padding)

    # Write Trade Codes: <And add every trade code
    #text_coord = (x_offset + padding, y_offset + padding)
    text_coord = (b1[0][0] + x_alignment, b1[0][1], y_alignment)
    legend_draw.text(text_coord, text, font_color, font=font)

    # Add text purchase info and sell info.
    # text = 'Trade goods'
    # x, y = font.getsize(text)
    # text_x_alignment = int((legend_width/4 - x)/2)
    # text_y_alignment = int((legend_width * 3/48 - y)/2)
    # text_coord = (x_offset + text_x_alignment , y_offset + text_y_alignment + (legend_width * 3/48))
    # legend_draw.text(text_coord, text, font_color, font=font)

    # text = 'Purchase DM | Sell DM'
    # x, y = font.getsize(text)
    # text_coord = (x_offset + legend_width/4 +text_x_alignment , y_offset + text_y_alignment + (legend_width * 3/48))
    # legend_draw.text(text_coord, text, font_color, font=font)

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