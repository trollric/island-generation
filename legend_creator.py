# Takes an UPP dictionary (Universal planetary profile) and cretes a map legend
# This include descriptive name of the different colors, goverment type, temperature range,
# Atmosphearic demands, Startport quality and trade codes.
import json
import os
import colors
import io
import math
import matplotlib.pyplot as plt
import numpy as np
from planet_generator import create_color_palette
from planet_generator import upp_to_dict
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from random import choice as random_choice
from random import randint


# Constants
FONT_PATH = "Fonts/Optima-LT-Medium-Italic.ttf"
FONT_COLOR = tuple(colors.get_rgb_color('black'))
LINE_COLOR = tuple(colors.get_rgb_color('black'))
BACKGROUND_COLOR = tuple(colors.get_rgb_color('dim_gray', 0))
LINE_WIDTH = 12


class BoundBox:
    """Contains a start and end point spanning a bound box. With various helper functions for
    getting dimensions, moving the box etc.
    """
    def __init__(self, x1:int, y1:int, x2:int, y2:int):
        """Creates the bound objects start and endpoint.

        Args:
            x1 (int): start value for x
            x2 (int): end value for x
            y1 (int): start value y
            y2 (int): end value y

        Raises:
            ValueError: Returns an error if the start value of any type is bigger than the end
            value.
        """
        if x1 > x2 or y1 > y2:
            raise ValueError(f'''the start point values can not be smaller than the end point values.\n
                                Provided x1: {x1}, x2: {x2}, y1: {y1}, y2: {y2} ''')
        self.start = (x1, y1)
        self.end = (x2, y2)

    def get_width(self):
        """Returns the width of the bound box

        Returns:
            int: width of the box
        """
        return self.end[0] - self.start[0]

    def get_height(self):
        """Returns the height of the bound box object

        Returns:
            int: height of the bouind box
        """
        return self.end[1] - self.start[1]

    def get_width_height(self):
        """Provides the BoundBox width/height as tuple.

        Returns:
            tuple(int, int): Width/Height as a tuple.
        """
        return (self.get_width(), self.get_height())

    def get_dimensions(self):
        """Returns the start and end point as a list of tuples

        Returns:
            list: returns a list of two tuples.
        """
        return [tuple(self.start), tuple(self.end)]

    def get_side(self, side : str) -> int:
        """Returns the provided sides value

        Args:
            side (str): side to be returns ['left', 'top', 'right', 'bottom']

        Raises:
            ValueError: If the value is not a side.
            TypeError: If the provided value is not a string.

        Returns:
            int: The value of the side asked for.
        """
        if not isinstance(side, str):
            raise TypeError('Provided side needs to be a string')
        if side.lower() not in ['left', 'top', 'right', 'bottom']:
            raise ValueError('Provided string is not "left", "top", "right" or "bottom"')
        value = 0
        if side.lower() == 'left':
            value = self.start[0]
        elif side.lower() == 'top':
            value = self.start[1]
        elif side.lower() == 'right':
            value = self.end[0]
        elif side.lower() == 'bottom':
            value = self.end[1]
        
        return value

    def set_anchor(self, anchor: tuple[int, int]):
        """Moves the anchor point to the new anchor.

        Args:
            anchor (tuple[int, int]): tuple containing the new x,y coordinate.

        Raises:
            TypeError: anchor must be a tuple.
            TypeError: may only contain two values.
            ValueError: both values must be of type int.
            ValueError: both values must be a positive integer
        """
        # Check that anchor is of type tuple.
        if not isinstance(anchor, tuple):
            raise TypeError('anchor must be be a tuple of type tuple.\n'+
                            f'type of anchor: {type(anchor)}')

        # Check that the tuple anchor is of the correct lenght.
        if len(anchor) != 2:
            raise TypeError('acnhor must be a tuple with two elements.\n'+
                            f'Length of anchor: {len(anchor)}')
        
        # Check that the values in anchor are of type int.
        if not all(isinstance(value, int) for value in anchor):
            raise ValueError('anchor must be of type (int, int).\n'+
                            f'Provided: ({type(anchor[0])}, {type(anchor[1])})')

        # Check that no value is negative.
        if not all(value >= 0 for value in anchor):
            raise ValueError('Both the x and y value of anchor must be positive.\n'+
                            f'Provided: x: {anchor[0]}, y: {anchor[1]}')


        # Get the coordinates for the bound box
        x1, y1 = self.start
        x2, y2 = self.end

        # New start coordinate.
        anchor_x, anchor_y = anchor

        # Calculte the move vector to get from the old anchor point.
        # to the new acnhor point
        move_x, move_y = anchor_x - x1, anchor_y - y1

        # Move the bound box to start at anchor and span the same
        # height and width
        self.start  = (x1 + move_x, y1 + move_y)
        self.end    = (x2 + move_x, y2 + move_y)

    def split(self, vertical_splits: int = 1, horizontal_splits: int = 1) -> list:
        """Splits the box into an 2D-array of BoundBoxes.\n
        Example:\n
        b1 = BoundBox(0, 0, 100, 100)\n
        sub_boxes = b1.split(2, 2)\n
        sub_boxes[0][0].start => (0, 0)\n
        sub_boxes[0][0].end => (50, 50)\n
        sub_boxes[1][1].start => (50, 50)\n
        sub_boxes[1][1].end => (100, 100)

        Args:
            vertical_splits (int, optional): Determines how many boxes will be created on the x-axis. Defaults to 1.
            horizontal_splits (int, optional): Determines how many boxes will be created on the y-axis. Defaults to 1.

        Raises:
            TypeError: Both parameters must be integers.
            ValueError: Both parameters must be greater than 0.

        Returns:
            list: list[list[BoundBox]]
        """
        # Check the parameter types.
        if not all(isinstance(parameter, int) for parameter in [vertical_splits, horizontal_splits]):
            raise TypeError('Both parameters needs to be of type int.\n'+
                            f'Types provided: (x: {type(vertical_splits)}, y:{type(horizontal_splits)})')

        # Check that both values are greater than zero
        if not all(values > 0 for values in [vertical_splits, horizontal_splits]):
            raise ValueError('Both parameters needs to be greater than 0.\n'+
                            f'Provided values (x: {vertical_splits}, y: {horizontal_splits})')


        # calculate width/height of the subboxes.
        width, height = self.get_width_height()

        sub_width = int(width / vertical_splits)
        sub_height = int(height / horizontal_splits)


        # populate the 2D-list with subboxes.
        # Set parameters
        sub_box_list = []
        x1, start_y = self.start

        # Loop through every x-position.
        for _ in range(vertical_splits):
            # Reset parameters
            vertical_elements = []
            y1 = start_y

            # Create the next set of subboxes for the y-positions.
            for _ in range(horizontal_splits):
                # Add vertical subbox
                vertical_elements.append(BoundBox(x1, y1, x1 + sub_width, y1 + sub_height))

                # Adjust anchor for the next subbox.
                y1 += sub_height
            
            # append set of y-positions to the current x.
            sub_box_list.append(vertical_elements)

            # Adjust the anchor for the next set of subboxes
            x1 += sub_width

        return sub_box_list


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


def percent_of_number(num, percentage) -> float:
    """Takes a number and percentage and returns the percentage part of that
    number.

    Args:
        num (float, int): a float or integer value
        percentage (float, int): float or integer representing a percentage between
        0.0 - 100.0. If the value is out of bounds it will be mapped to 0 or 100.

    Returns:
        float: part of the number
    """
    if not isinstance(num, (float, int)):
        raise TypeError('num must be of float or integer type.')

    if not isinstance(percentage, (float, int)):
        raise TypeError('percentage must be of int or float value')

    if percentage < 0.0:
        percentage = 0
    elif percentage > 100:
        percentage = 100
        
    return int(num * (percentage / 100))


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
    with open("Data/trade_code_classification.json",) as trade_requirement_data:
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


    # Draw the legnd boundary lines.
    legend_draw.rectangle([(0, 0), (legend_width, legend_height)],
                                    outline=LINE_COLOR,
                                    fill=BACKGROUND_COLOR,
                                    width=LINE_WIDTH)
    
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

    # Draw a line from the middle of the paper to the right
    lines.append([(x, y*17), (legend_width, y*17)])

    # Separator all the way down.
    lines.append([(x, y*14), (x, legend_height)])

    # Add a divider inside the trade box
    half_box_y = int(y*3/2)
    lines.append([(x, y*14 + half_box_y), (legend_width, y*14 + half_box_y)])
    # Add separator for Buy/Sell tabs.
    lines.append([(int(x*3/2), y*14 + half_box_y), (int(x*3/2), legend_height)])


    # Draw all lines 
    for line in lines:
        legend_draw.line(line, fill=LINE_COLOR, width=LINE_WIDTH)

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
        and availability status as bool.
    """
    # Check that trade_codes is a list.
    if not isinstance(trade_codes, list):
        raise TypeError('Trade codes needs to be a list of traveler trade codes.')
    
    # Check that all values inside trade_codes are trade codes.
    if not validate_trade_codes(trade_codes):
        raise TypeError(f'One or more trade codes are not valid.\nCodes: {trade_codes}')

    # Import the json-data
    with open("Data/trade_goods_table.json",) as trade_goods_data:
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
                if goods_data.get('purchase_dm').get(code) > purchase_dm:
                    purchase_dm = goods_data.get('purchase_dm').get(code)

            # If there is a sell dm save the highest one applicable.
            if not goods_data.get('sale_dm').get(code) == None:
                if goods_data.get('sale_dm').get(code) > sell_dm:
                    sell_dm = goods_data.get('sale_dm').get(code)
        
        # If available and a buy or sell dm exist save the highest one that occured
        if available or purchase_dm > 0 or sell_dm > 0:
            trade_goods.update({type : {'purchase_dm' : purchase_dm, 'sale_dm' : sell_dm,
                                        'availability' : available}})


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
    """ LEGACY: Use BoundBox get_dimension() function instead.
    Takes a box_dimension and returns width, height as a tuple.

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


def get_text_dimensions(text_string, font):
    """Takes a text and font and returns the width, height values of the close box

    Args:
        text_string (str): text to be rendered
        font (FreeTypeFont): The font to be used.

    Returns:
        tuple(int, int): width,height
    """
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = int(font.getmask(text_string).getbbox()[2])
    text_height = int(font.getmask(text_string).getbbox()[3] + descent)

    return (text_width, text_height)


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
    text_width, text_height = get_text_dimensions(text, font)

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

    # Look at the y center alignment. Text is slightly off center.
    # Calculated adjustment_y
    if vertical.lower() == 'top':
        adjustment_y = padding[1]
    elif vertical.lower() == 'center':
        adjustment_y = int((height - text_height) / 2)
    elif vertical.lower() == 'bottom':
        adjustment_y = height - (text_height + padding[1])

    return adjustment_x, adjustment_y


def get_max_font_size(box_dimensions, text, font_path, padding = 0):
    """Takes a bounding box and returns the largest possible font size. If you wish to 
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
    elif not padding >= 0:
        raise ValueError(f'padding must be a positive integer. Provided value: {padding}')

    # Try every font size from 1-400 until text_width or text_height is larger than the bounding box.
    font_size = 1
    width, height = get_box_dimension_size(box_dimensions)
    for size in range(1, 401):
        font = ImageFont.truetype(font_path, size)
        x1, y1, x2, y2 = font.getbbox(text)
        text_width = x2 - x1
        text_height = y2 - y1

        # Break if we have reached the largest font size possible.
        if text_width > width - 2 * padding or text_height > height - 2 * padding:
            break

        font_size = size

    return font_size


def get_multiline_max_font_size(box_dimensions, text, font_path, padding = 0, spacing = 4.0):
    """Returns the largest font size for given font and multiline text to fit inside
    BoundBox or a box_dimension. Padding and spacing are optional.

    Args:
        box_dimensions (BoundBox/list[int, int, int, int], tuple(width, height),
        list[tuple(int, int), (int, int)]): Box dimension or BoundBox
        text (str): Multiline string. If a non multiline string is given it gets passed on to
        get_max_font_size
        font_path (str): path to the desired font.
        padding (int, optional): Ensurs the value fits inside padding. Defaults to 0.
        spacing (float, optional): Distance between lines. Defaults to 4.0.

    Raises:
        TypeError: text needs to be of type string
        TypeError: font_path needs to be of type string.
        FileNotFoundError: Font path needs to point to an existing file.
        TypeError: padding needs to be of type in.
        ValueError: padding can not be negative.
        TypeError: spacing must be of type float.
        ValueError: spacing must be a positive number.

    Returns:
        int: maximum font size that fits inside given dimensions.
    """
    # If a BoundBox is not given. Convert the dimensions to a boundbox.
    if not isinstance(box_dimensions, BoundBox):
        # Check if box_dimensions are valid
        validate_box_dimensions(box_dimensions)

        # Create a bound box from the box_dimensions.
        if isinstance(box_dimensions, tuple):
            width, height = box_dimensions
        elif len(box_dimensions) == 2:
            width = box_dimensions[1][0] - box_dimensions[0][0]
            height = box_dimensions[1][1] - box_dimensions[0][1]
        elif len(box_dimensions) == 4:
            width = box_dimensions[0] - box_dimensions[2]
            height = box_dimensions[1] - box_dimensions[3]
        sub_box = BoundBox(0, 0, width, height)
    else:
        sub_box = BoundBox(0, 0, box_dimensions.get_width(), box_dimensions.get_height())

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
    elif not padding >= 0:
        raise ValueError(f'padding must be a positive integer. Provided value: {padding}')

    # Validate spacing type.
    if not isinstance(spacing, float):
        raise TypeError(f'spacing was not of type float. Type provided: {type(spacing)}')
    elif spacing < 0.0:
        raise ValueError(f'spacing must be greater than 0. spacing value: {spacing}')
    
    # Check if the text is a multiline string. Delegate to get_max_font_size() if it is.
    if not('\n' in text or '\r' in text):
        return get_max_font_size(sub_box.get_dimensions(), text, font_path, padding)

    
    # Try every font size from 1-400 until text_width or text_height is larger than the bounding box.
    font_size = 1
    xy = (0, 0)
    width, height = sub_box.get_width_height()
    image = Image.new('RGBA', (width, height))
    imDraw = ImageDraw.ImageDraw(image)

    for size in range(1, 401):
        font = ImageFont.truetype(font_path, size)
        x1, y1, x2, y2 = imDraw.multiline_textbbox(xy, text, font=font, spacing=spacing)
        text_width = x2 - x1
        text_height = y2 - y1

        # Break if we have reached the largest font size possible.
        if text_width > width - 2 * padding or text_height > height - 2 * padding:
            break

        font_size = size

    return font_size


def draw_text_bound_box(bound_box : BoundBox, text : str, font_path : str, draw : ImageDraw.ImageDraw,
                        font_color : tuple, padding : int = 0, spacing : float = 4.0,
                        font_size : int = 0, text_alignment : str = 'left',
                        horizontal_alignment : str = 'left', vertical_alignment : str = 'top'):
    """Writes a multiline string inside a BoundBox. If no font_size is given it fills the BoundBox
    as much as possible taking padding and spacing into consideration.

    Args:
        bound_box (BoundBox): The box where the text will be written.
        text (str): Multiline text to write.
        font_path (str): path to the font type to be used.
        draw (ImageDraw.ImageDraw): draw context.
        font_color (tuple): RGB or RGBA color.
        padding (int, optional): padding from the top and left side.. Defaults to 0.
        spacing (float, optional): space between lines. Defaults to 4.0.
        font_size (int, optional): Set font size. If no value is given maximum font size is
        calculated automatically.
        text_alignment (str, optional): Set font alignment (left, center, right). Defaults to left.
        horizontal_alignment (str, optional): (left, center, right). Aligns the text horizontally
        inside the box.
        vertical_alignment (str, optional): (top, center, bottom). Aligns the text vertically inside
        the box.

    Raises:
        TypeError: Bound box needs to be of type BoundBox
        TypeError: text and font_path needs to be of type string.
        FileNotFoundError: If the font at font_path is not found.
        TypeError: draw context needs to be of ImageDraw class.
        TypeError: font_color needs to be of type tuple.
        ValueError: font_color tuple needs to be of length 3 or 4.
        TypeError: values provided in font_color tuple needs to be 8bit integers.
        TypeError: padding must be of type int.
        ValueError: padding can not be negative.
        TypeError: spacing needs to be of type float.
        ValueError: spacing can not be negative.
        TypeError: text_alignment needs to be of type string.
        ValueError: text_alignment must be (left, center or right).
        TypeError: horizontal_alignment needs to be of type string.
        ValueError: horizontal_alignment must be (left, center or right).
        TypeError: vertical_alignment needs to be of type string.
        ValueError: vertical_alignment must be (top, center or bottom).
    """

    # Validate paramters.
    if not isinstance(bound_box, BoundBox):
        raise TypeError(f'bound_box was not a BoundBox. Type provided: {type(bound_box)}')

    # Check that text and font path are of type string.
    if not all(isinstance(parameter, str) for parameter in [text, font_path]):
        raise TypeError(f'''text or font_path must be string. text: {type(text)}, 
        font_path {type(font_path)}''')

    # Verify that the file at font_path exist.
    if not os.path.exists(font_path):
        raise FileNotFoundError(f'''font_path does not provide a path to an existing file.\n
        path provided: {font_path}''')

    # Verify draw.
    if not isinstance(draw, ImageDraw.ImageDraw):
        raise TypeError(f'draw needs to be of type ImageDraw. draw type: {type(draw)}')

    # Verify font_color
    if not isinstance(font_color, tuple):
        raise TypeError(f'font_color needs a tuple. font_color type: {type(font_color)}')
    elif not(3 <= len(font_color) <= 4):
        raise ValueError(f'''Tuple needs to be three or four 8-bit integers long.\n
        tuple length: {len(font_color)}''')
    elif not all(isinstance(value, int) for value in font_color):
        raise TypeError(f'Not all values in font_colors were of type int. font_color: {font_color}')
    
    # Verify padding.
    if not isinstance(padding, int):
        raise TypeError(f'padding not of type int. Type provided {type(padding)}')
    elif not padding >= 0:
        raise ValueError(f'padding can not be a negative number. padding provided: {padding}')

    # Verify spacing
    if not isinstance(spacing, float):
        raise TypeError(f'spacing is not of type float. Provided type {type(spacing)}')
    elif not spacing >= 0.0:
        raise ValueError(f'spacing can not be negative number. spacing provided: {spacing}')

    if not isinstance(font_size, int):
        raise TypeError(f'font_size needs to be of type integer. Type provided: {type(font_size)}')
    elif not font_size >= 0:
        raise ValueError(f'padding can not be a negative number. padding provided: {font_size}')

    # Verify alignments.
    # text.
    if not isinstance(text_alignment, str):
        raise TypeError(f'alignment needs to be of type string.\nProvided type {type(text_alignment)}')
    elif not text_alignment in ['left', 'center', 'right']:
        raise ValueError(f'''alignment needs to be (left, center or right).\n
                        Provided value: {text_alignment}''')

    # horizontal.
    if not isinstance(horizontal_alignment, str):
        raise TypeError(f'''alignment needs to be of type string.\n
        Provided type: {type(horizontal_alignment)}''')
    elif not horizontal_alignment in ['left', 'center', 'right']:
        raise ValueError(f'''alignment needs to be (left, center or right).\n
                        Provided value: {horizontal_alignment}''')

    # vertical.
    if not isinstance(vertical_alignment, str):
        raise TypeError(f'''alignment needs to be of type string.\n
        Provided type: {type(vertical_alignment)}''')
    elif not vertical_alignment in ['top', 'center', 'bottom']:
        raise ValueError(f'''alignment needs to be (left, center or right).\n
                        Provided value: {vertical_alignment}''')

    # If font size is not provided. Get the maximum font size that will fit in the box.
    if font_size == 0:
        font_size = get_multiline_max_font_size(bound_box, text, font_path, padding, spacing)

    # Create font.
    font = ImageFont.truetype(font_path, font_size)

    # Get anchor position.
    x1 = bound_box.get_side('left')
    y1 = bound_box.get_side('top') + padding

    # Get text box dimensions.
    xy = (0,0)
    image = Image.new('RGBA', bound_box.get_width_height())
    imDraw = ImageDraw.ImageDraw(image)

    text_x1, text_y1, text_x2, text_y2 = imDraw.multiline_textbbox(xy, text, font, spacing=spacing)
    text_width = text_x2 - text_x1
    text_height = text_y2 - text_y1

    if horizontal_alignment == 'left':
        x1 += padding
    elif horizontal_alignment == 'center':
        x1 += int((bound_box.get_width() - text_width) / 2)
    elif horizontal_alignment == 'right':
        x1 = bound_box.get_side('right') - (text_width + padding)

    if vertical_alignment == 'top':
        y1 += padding
    elif vertical_alignment == 'center':
        y1 += int((bound_box.get_height() - text_height) / 2)
    elif vertical_alignment == 'bottom':
        y1 += bound_box.get_side('bottom') - (text_height + padding)


    # Draw the text.
    draw.multiline_text((x1, y1), text, font_color, font, spacing=spacing, align=text_alignment)


def get_max_font_size_from_list(list, font_path, box_dimensions, padding = 0):
    """Takes a list of lines and checks what their maxiumum shared font_size can be.
    If they are to fit in boxes of the same size.

    Args:
        list (list): List of strings to be evaluated.
        font_path (string): Path to desired font to check against
        box_dimensions (list of tuples): list of tuples [(x1, y1), (x2, y2)]
        padding (int, optional): Take padding into consideration. Defaults to 0.

    Returns:
        int: Font size as an integer.
    """
    font_size = None
    for line in list:
        sub_font_size = get_max_font_size(box_dimensions, line, font_path, padding)
        if font_size == None or sub_font_size < font_size:
            font_size = sub_font_size
    return font_size


def draw_text_in_list(legend_draw, font, font_color, box_dimensions, list, padding = 0,
                        vertical = 'center', horizontal = 'left'):
    """Renders every text line in the list on separate lines.

    Args:
        legend_draw (ImageDraw): ImageDraw class with reference to image to be rendered on.
        font (FreeTypeFont): FreeTypeFont object containing font and font_size
        font_color (tuple): Tuple containing RGBA information.
        box_dimensions (list, tuples): List of tuples containing boundbox dimensions.
        list (list): List of strings.
        padding (int, optional): Take padding into consideration as needed. Defaults to 0.
        vertical (string, optional): Set vertical alignment (top, center, bottom) Defaults to center.
        horizontal (string, optional): Set horizontal alignment (left, center, right) Defaults to
        right. 
    """
    # Draw every line in list.
    _, y_offset = box_dimensions[0]
    for line in list:
        # Get text alignments for the box dimensions.
        x_alignment, y_alignment = get_font_align_offsets(  box_dimensions, line, font,
                                                            vertical=vertical,
                                                            horizontal=horizontal,
                                                            padding=padding)
        text_coord = (box_dimensions[0][0] + x_alignment, y_offset + y_alignment)
        # Render the text
        legend_draw.text(text_coord, line, font_color, font=font)
            
        # Increment the box_dimensions offset..
        y_offset += (box_dimensions[1][1] - box_dimensions [0][1])


def roll_2d():
    """Rolls two six sided dies and returns the sum rolled.

    Returns:
        int: Sum of the two dice rolled.
    """
    dice1 = randint(1,6)
    dice2 = randint(1,6)

    return dice1 + dice2


def roll_d66():
    """Rolls two six sided dies with one representing the ones and one representing the tens

    Returns:
        int: 11-16, 21-26, 31-36, 41-46, 51-56, 61-66
    """
    dice1 = int(randint(1,6) * 10)
    dice2 = randint(1,6)

    return dice1 + dice2


def legend_append_trade_codes(legend_image, trade_codes):
    """Takes a legend_image from the create_legend image function
    and appends all viable trade data determined by trade_codes

    Args:
        legend_image (PIL.Image): legend image containing layout for the data.
        trade_codes (list): List of the trade codes that are applicable to the planet.

    Raises:
        ValueError: If a font size can not be generated for the b4 bounding box. Raise a value
        error.

    Returns:
        PIL.Image: Returns the legend image with appended trade code data.
    """
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

    #TODO: Could be improved by determining contraband and goods produced
    # and giving these trade goods a special color accordingly.

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
    padding = 20

    # Create a font for the trade_string
    trade_string = ', '.join(trade_codes)
    text = f'Trade codes: {trade_string}'
    
    # Determine maxiumum font size with padding.
    font_size = get_max_font_size(b1, text, FONT_PATH, padding)
    font = ImageFont.truetype(FONT_PATH, font_size)

    x_alignment, y_alignment = get_font_align_offsets(  b1, text, font,
                                                        vertical='center',
                                                        padding=padding)

    # Write Trade Codes: And add every trade code
    text_coord = (b1[0][0] + x_alignment, b1[0][1] + y_alignment)
    legend_draw.text(text_coord, text, FONT_COLOR, font=font)

    # Add text purchase info and sell info.
    # Get maximum font size for b2 and create font.
    text = 'Trade goods'
    font_size = get_max_font_size(b2, text, FONT_PATH, padding)
    font = ImageFont.truetype(FONT_PATH, font_size)

    x_alignment, y_alignment = get_font_align_offsets(  b2, text, font,
                                                        vertical='center',
                                                        padding=padding)

    text_coord = (b2[0][0] + x_alignment , b2[0][1] + y_alignment)
    legend_draw.text(text_coord, text, FONT_COLOR, font=font)

    text = 'Purchase | Sell DM'
    font_size = get_max_font_size(b3, text, FONT_PATH, padding)
    font = ImageFont.truetype(FONT_PATH, font_size)

    x_alignment, y_alignment = get_font_align_offsets(  b3, text, font,
                                                        horizontal='center',
                                                        vertical='center',
                                                        padding=padding)

    text_coord = (b3[0][0] + x_alignment, b3[0][1] + y_alignment)
    legend_draw.text(text_coord, text, FONT_COLOR, font=font)

    # Get which types of trade goods should be appended.
    eligible_trade_goods = get_trade_goods(trade_codes)

    # Divide the height of b4 in equally large boxes.
    # Make space for a 1px padding for each box.
    # height / (len(trade codes) + (len(trade codes) + 1) * padding)
    number_of_codes = len(eligible_trade_goods)
    padding = 10
    b4_width, b4_height = get_box_dimension_size(b4)

    sub_box_height = int(b4_height / number_of_codes)
    sub_box = (b4_width, sub_box_height)


    # Append trade codes in the bottom right.
    # Find the largest font size possible that fits all boxes.
    font_size = None
    for text in eligible_trade_goods.keys():
        sub_font_size = get_max_font_size(sub_box, text, FONT_PATH, padding)
        if font_size == None or sub_font_size < font_size:
            font_size = sub_font_size

    if font_size == None:
        raise ValueError(f'''Something went wrong when trying to assign a font size.\n
                            there are to many trade goods to fit or padding is to large.\n
                            font_size: {font_size}, padding: {padding}''')

    # Create the font with the largest font_size that will fit.
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Assign special padding to the sub boxes of b5.
    b5_width, _ = get_box_dimension_size(b5)
    b5_padding = int(b5_width / 3)

    # Set startoffset for the sub boxes. ( They share y_offset)
    x_offset_b4, y_offset = (b4[0][0], b4[0][1])
    x_offset_b5 = b5[0][0]
    for key, value in eligible_trade_goods.items():
        # Get text alignment for the b4 sub box and draw the text.
        x_alignment, y_alignment = get_font_align_offsets(  sub_box, key, font,
                                                            vertical='center',
                                                            padding=padding)
        text_coord = (x_offset_b4 + x_alignment, y_offset + y_alignment)
        legend_draw.text(text_coord, key, FONT_COLOR, font=font)

        # If purchase dm is not 0
        # Get alignment and draw purchase_dm in b5
        purchase_dm = value.get('purchase_dm')
        if not purchase_dm == 0:
            x_alignment, _ = get_font_align_offsets(  sub_box, str(purchase_dm), font,
                                                                padding=b5_padding)
            text_coord = (x_offset_b5 + x_alignment, y_offset + y_alignment)
            legend_draw.text(text_coord, f'{purchase_dm}', FONT_COLOR, font=font)

        # If sale is not 0
        # Get alignment and draw sale_dm in b5
        sale_dm = value.get('sale_dm')
        if not sale_dm == 0:
            x_alignment, _ = get_font_align_offsets(  sub_box, str(sale_dm), font,
                                                                horizontal='right',
                                                                padding=b5_padding)
            text_coord = (x_offset_b5 + x_alignment, y_offset + y_alignment)
            legend_draw.text(text_coord, f'{sale_dm}', FONT_COLOR, font=font)
            
        # Increment the sub_box_offset.
        y_offset += sub_box_height
        
    return legend_image


def legend_append_planetary_metrics(legend_image, upp_dict):
    """Adds planetary metrics to the top middle of the legend document.
    Metrics like: Gravity, temperature etc.

    Args:
        legend_image (Image.Image): Image containing the legend document information.
        upp_dict (dict): dictionary with all UPP-data.

    Returns:
        Image.Image: PIL.Image with planetary metrics.
    """
    # Calculates planetary metrics using the upp_dict.
    #|-------------------------------------|
    #|b1                                   |
    #|                                     |
    #|                                     |
    #|                                     |
    #|-------------------------------------|
    #|b2             |b3                   |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|               |                     |
    #|-------------------------------------|
    
    # Get legend image dimensions.
    legend_width, _ = legend_image.size
    # Get size of the sum of b1, b2, b3
    # Also get different width values usefull in determining
    # the size and offset for the other boxes.
    x_box = int(legend_width/3)
    x_third_box = int(x_box/3)
    y_box = int(legend_width/3)
    y_third_box = int(y_box/3)

    # Get offset values to the upper left corner of b1.
    x_offset = x_box
    y_offset = 0

    # Create the bound boxes
    b1 = BoundBox(  x_offset, y_offset, x_offset + x_box, y_offset + y_third_box)
    b2 = BoundBox(  x_offset, b1.get_side('bottom'),
                    x_offset + x_third_box, b1.get_side('bottom') + 2*y_third_box)
    b3 = BoundBox(  b2.get_side('right'), b1.get_side('bottom'), b1.get_side('right'),
                    b2.get_side('bottom'))
    
    # Create draw object
    legend_draw = ImageDraw.Draw(legend_image)

    # Save font data.
    padding = 15

    # Create a subbox for the three lines in b1.
    x1 ,y1 = b1.start
    sub_box_b1 = BoundBox(x1, y1, x1 + b1.get_width(), y1 + int(b1.get_height()/3))

    # Get diamater and gravity data.
    diamater = None
    gravity = None
    size = upp_dict.get('size')

    # TODO: This data could be added as JSON database with int keys. Reducing the amount of lines
    # used.
    if size == 0:
        diamater = randint(500, 100)
        gravity = 'Negligible'
    elif size == 1:
        diamater = randint(1100,2200)
        gravity = '0.05 G'
    elif size == 2:
        diamater = randint(2800,3600)
        gravity = '0.15 G'
    elif size == 3:
        diamater = randint(4400,5200)
        gravity = '0.25 G'
    elif size == 4:
        diamater = randint(6000,6800)
        gravity = '0.35 G'
    elif size == 5:
        diamater = randint(7600,8400)
        gravity = '0.45 G'
    elif size == 6:
        diamater = randint(9200,10000)
        gravity = '0.7 G'
    elif size == 7:
        diamater = randint(10800,11600)
        gravity = '0.9 G'
    elif size == 8:
        diamater = randint(12400,13200)
        gravity = '1.0 G'
    elif size == 9:
        diamater = randint(14000,14800)
        gravity = '1.25 G'
    elif size == 10:
        diamater = randint(15600,16400)
        gravity = '1.4 G'
    
    # TODO: This data could be added as JSON database with int keys. Reducing the amount of lines
    # used.
    # Get population data.
    population = None
    upp_population = upp_dict.get('population')

    if upp_population == 0:
        population = 'None'
    elif upp_population == 1:
        population = 'Few'
    elif upp_population == 2:
        population = 'Hundreds'
    elif upp_population == 3:
        population = 'Thousands'
    elif upp_population == 4:
        population = 'Tens of thousands'
    elif upp_population == 5:
        population = 'Hundreds of thousands'
    elif upp_population == 6:
        population = 'Millions'
    elif upp_population == 7:
        population = 'Tens of millions'
    elif upp_population == 8:
        population = 'Hundreds of millions'
    elif upp_population == 9:
        population = 'Billions'
    elif upp_population == 10:
        population = 'Tens of billions'
    elif upp_population == 11:
        population = 'Hundred of billions'
    elif upp_population == 12:
        population = 'Trillions, World-Ciy'


    # Create datastrings in a list.
    size_and_population_metrics =[
        f'Diameter: {diamater} km',
        f'Gravity: {gravity}',
        f'Population: {population}',
    ]

    font_size = get_max_font_size_from_list(size_and_population_metrics,
                                                FONT_PATH,
                                                sub_box_b1.get_dimensions(),
                                                padding)

    # Create font
    font = ImageFont.truetype(FONT_PATH, font_size)
    
    # Draw size and population data.
    draw_text_in_list( legend_draw, font, FONT_COLOR, sub_box_b1.get_dimensions(),
                        size_and_population_metrics, padding)

    # TODO: This data could be added as JSON database with int keys. Reducing the amount of lines
    # used.
    # Get atmospheric data
    atmosphere = None
    ppe_required = None
    atmosphere_type = upp_dict.get('atmosphere_type')
    if atmosphere_type == 0:
        atmosphere = 'None'
        ppe_required = 'Vacc Suit'
    elif atmosphere_type == 1:
        atmosphere = 'Trace'
        ppe_required = 'Vacc Suit'
    elif atmosphere_type == 2:
        atmosphere = 'Very Thin, Tainted'
        ppe_required = 'Respirator, Filter'
    elif atmosphere_type == 3:
        atmosphere = 'Very Thin'
        ppe_required = 'Respirator'
    elif atmosphere_type == 4:
        atmosphere = 'Thin, Tainted'
        ppe_required = 'Filter'
    elif atmosphere_type == 5:
        atmosphere = 'Thin'
        ppe_required = 'None'
    elif atmosphere_type == 6:
        atmosphere = 'Standard, Tainted'
        ppe_required = 'None'
    elif atmosphere_type == 7:
        atmosphere = 'Standard, Tainted'
        ppe_required = 'Filter'
    elif atmosphere_type == 8:
        atmosphere = 'Dense'
        ppe_required = 'None'
    elif atmosphere_type == 9:
        atmosphere = 'Dense, Tainted'
        ppe_required = 'Filter'
    elif atmosphere_type == 10:
        atmosphere = 'Exotic'
        ppe_required = 'Air Supply'
    elif atmosphere_type == 11:
        atmosphere = 'Corrosive'
        ppe_required = 'Vacc Suit'
    elif atmosphere_type == 12:
        atmosphere = 'Insidious'
        ppe_required = 'Vacc Suit'
    elif atmosphere_type == 13:
        atmosphere = 'Very Dense'
        ppe_required = 'None'
    elif atmosphere_type == 14:
        atmosphere = 'Low'
        ppe_required = 'None'
    elif atmosphere_type == 15:
        atmosphere = 'Unusual'
        ppe_required = 'Varies'
    

    # Generate the min/max temperature and determine day/night cycle.
    day_length = 8 + 8 * upp_dict.get('size') + randint(-4, 4)

    min_temperature, max_temperature = None, None
    temp_info = upp_dict.get('temperature')
    if temp_info == 'frozen':
        min_temperature = randint(-273, -70)
        max_temperature = randint(-60, -51)
    elif temp_info == 'cold':
        min_temperature = randint(-51, -25)
        max_temperature = randint(-20, 0)
    elif temp_info == 'temperate':
        min_temperature = randint(-5, 1)
        max_temperature = randint(20, 30)
    elif temp_info == 'hot':
        min_temperature = randint(27, 40)
        max_temperature = randint(63, 80)
    elif temp_info == 'boiling':
        min_temperature = randint(81, 90)
        max_temperature = randint(176, 800)

    # Make the string data
    planetary_metrics =[
        f'Atmosphere:',
        f'{atmosphere}',
        f'PPE Required:',
        f'{ppe_required}',
        f'Temperature:',
        f'Min: {min_temperature} [C]',
        f'Max: {max_temperature} [C]',
        f'Day cycle:',
        f'{day_length} [h]'
    ]

    # Create sub box.
    x1, y1  = b2.start
    x2, _   = b2.end
    y2 = y1 + int(b2.get_height() / len(planetary_metrics))
    sub_box_b2 = BoundBox(x1, y1, x2, y2)

    # Find largest font size
    font_size = get_max_font_size_from_list(planetary_metrics,
                                                FONT_PATH,
                                                sub_box_b2.get_dimensions(),
                                                padding=8)

    # Create the font
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Render the data
    draw_text_in_list( legend_draw,
                        font,
                        FONT_COLOR,
                        sub_box_b2.get_dimensions(),
                        planetary_metrics,
                        padding)

    # Generate matplotlib graph to show temperature over a day/night cycle.
    # Make a timeline array
    time = np.arange(0, day_length, 0.05)

    # Make a vectorized function for calculatin temp(time)
    temp = np.vectorize(
        lambda x: min_temperature + abs(math.sin(math.pi*x/day_length) * (max_temperature - min_temperature))
    )

    # Build figure.
    figsize = (4.0, 4.0)

    # Set the desired style.
    with plt.style.context('dark_background'):
        figure = plt.figure(figsize=figsize)
        # Make the background transparent
        figure.set_alpha(0.0)

        ax = figure.add_subplot(111)

        # Set axis data.
        ax.set_title('Temperature over time')
        ax.set_ylabel('Temperature [C]')
        ax.set_xlabel(f'Day cycle {day_length} [h]')
    
        # Plot
        ax.plot(time, temp(time), 'r-', linewidth=1.5)
    

    figure.subplots_adjust(left=0.18, right=0.95, bottom=0.15, top=0.90)

    buffer = io.BytesIO()
    figure.savefig(buffer, facecolor=figure.get_facecolor())
    buffer.seek(0)
    
    plot_image = Image.open(buffer)

    # Resize plot_image to bound box3:s size.
    plot_image = plot_image.resize(b3.get_width_height())

    # Append plot_image into bound box b3
    legend_image.paste(plot_image, b3.start)

    # Reapply lines around the boundbox.
    # Custom line information.
    line_width = 4
    
    # Redraw a box around b2 and b3.
    legend_draw.rectangle(b2.get_dimensions(), outline=LINE_COLOR, width=line_width)
    legend_draw.rectangle(b3.get_dimensions(), outline=LINE_COLOR, width=line_width)

    return legend_image


def legend_append_planetary_image(legend_image : Image.Image , path : str) -> Image.Image:
    """Appends a generated planet at path to the legend document.

    Args:
        legend_image (Image.Image): Image to append the image onto.
        path (str): path to the image to be added.

    Raises:
        FileNotFoundError: If path does not point to an object raise an error.

    Returns:
        Image.Image: Legend image with appended planet.
    """
    # Test that image exist.
    if not os.path.exists(path):
        raise FileNotFoundError(f'The file at "{path}" could not be found')

    # Generate bound box
    legend_width, _ = legend_image.size
    x_offset = int(2*legend_width/3)
    y_offset = 0
    box_side = int(legend_width/3)

    bbox = BoundBox(x_offset, y_offset, x_offset + box_side, y_offset + box_side)

    # Load planetary image
    planet_image = Image.open(path)

    # Append in boundbox
    planet_image = planet_image.resize(bbox.get_width_height())
    legend_image.alpha_composite(planet_image, bbox.start)

    return legend_image


def legend_append_color_legend(legend_image, color_palette):
    """Adds a color legend to the middle right of the legend data sheet.

    Args:
        legend_image (PIL.Image): a PIL image containing legend data.
        color_palette (list(tuple(tuple(int,int,int,int), float, str))): list of tuples containing
        color data. (Color tuple, height float, terrain string)

    Returns:
        PIL.Image: Retuns the updated legend data image.
    """
    # Create main bound box.
    legend_width, _ = legend_image.size
    box_width = int(legend_width/3)
    box_height = int(legend_width/4)

    x_offset = box_width*2
    y_offset = box_width

    main_box = BoundBox(x_offset, y_offset, x_offset + box_width, y_offset + box_height)

    # Create draw object
    legend_draw = ImageDraw.Draw(legend_image)

    # Save font data.
    padding = 20

    # Calculate subbox size.
    sub_height = int(main_box.get_height() / len(color_palette))
    x1, y1 = main_box.start
    x2, _ = main_box.end
    y2 = y1 + sub_height
    
    sub_box = BoundBox(x1, y1, x2, y2)
    
    # Find largest font size.
    # Color palette examble (tuple list)
    # E.g. ('blue, 0.4, 'Water')
    text, color_list = [], []
    
    for color_string, _, line in color_palette:
        text.append(line.capitalize())
        color_list.append(color_string)

    font_size = get_max_font_size_from_list(text, FONT_PATH, sub_box.get_dimensions(), padding)

    # Create the font
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Print every element and add a colored box to the end of it.
    x, y = main_box.start
    for line, color in zip(text, color_list):
        x_align, y_align = get_font_align_offsets(  sub_box.get_dimensions(), line, font,
                                                    vertical='center', padding=padding)
        legend_draw.text((x_align + x, y_align + y), line, tuple(FONT_COLOR), font)

        # Draw colored Square
        square_side = int(font_size - 10)
        x_square_align = int(3*sub_box.get_width()/len(color_list))
        y_square_align = int((sub_box.get_height()-square_side)/2)
        x1 = x + x_square_align
        y1 = y + y_square_align
        x2 = x1 + square_side
        y2 = y1 + square_side

        legend_draw.rectangle(  (x1, y1, x2, y2),
                                fill=tuple(colors.get_rgb_color(color)),
                                outline=(0, 0, 0),
                                width=5)
        
        # Offset one more subbox
        y += sub_box.get_height()

    return legend_image


def legend_append_name_government_data(legend_image, planet_name, upp_dict):
    
    # ----------------------------------
    # | b1                             |
    # |                                |
    # |                                |
    # |                                |
    # ----------------------------------
    # | b2                             |
    # |                                |
    # |                                |
    # |                                |
    # ----------------------------------
    # | b3       | b4       | b5       |
    # |          |          |          |
    # |          |          |          |
    # |          |          |          |
    # ----------------------------------
    # b1: Planet name and UPP-Serial
    # b2: Government type
    # b3: Symbol depicting goverment type.
    # b4: Law level with a sheriffs badge behind.
    # b5: Tech level with circuit behind

    # Calculate sub box sizes.
    legend_width, _ = legend_image.size
    box_side = int(legend_width / 3)
    third_box_side = int(box_side / 3)

    # Create bound boxes
    x_offset, y_offset = (0, 0)
    b1 = BoundBox(x_offset, y_offset, x_offset + box_side, y_offset + third_box_side)

    y_offset = third_box_side
    b2 = BoundBox(x_offset, y_offset, x_offset + box_side, y_offset + third_box_side)

    y_offset = 2 * third_box_side
    b3 = BoundBox(x_offset, y_offset, x_offset + third_box_side, y_offset + third_box_side)

    x_offset += third_box_side
    b4 = BoundBox(x_offset, y_offset, x_offset + third_box_side, y_offset + third_box_side)

    x_offset += third_box_side
    b5 = BoundBox(x_offset, y_offset, x_offset + third_box_side, y_offset + third_box_side)
    # Create the draw class.
    legend_draw = ImageDraw.Draw(legend_image)

    # Font data.
    padding = 20

    # Make the text list.
    b1_data = [
        f'Name: {planet_name}',
        f'UPP:{upp_dict.get("upp_serial")}'
    ]

    # Create subbox
    x1, y1 = b1.start
    x2, _ = b1.end
    y2 = int((b1.get_height()/len(b1_data)) + y1)
    sub_box_b1 = BoundBox(x1, y1, x2, y2)
    
    # Create font
    font_size = get_max_font_size_from_list(b1_data, FONT_PATH, sub_box_b1.get_dimensions(), padding)
    font = ImageFont.truetype(FONT_PATH, font_size)

    draw_text_in_list(legend_draw, font, FONT_COLOR, sub_box_b1.get_dimensions(), b1_data, padding)

    # Get goverment type.
    # Import the json-data
    with open("Data/government_data.json",) as government_data:
        government_information = json.load(government_data)

    government_number = str(upp_dict.get('government_type'))
    government_dict = government_information.get(government_number)

    text = [f'Government type:',
            f"{government_dict.get('type')}"]

    # Write the information in b2.
    x1, y1  = b2.start
    x2, _  = b2.end
    y2 = int((b2.get_height()/len(text)) + y1)
    sub_box_b2 = BoundBox(x1, y1, x2, y2)

    font_size = get_max_font_size_from_list(text, FONT_PATH, sub_box_b2.get_dimensions(), padding)
    font = ImageFont.truetype(FONT_PATH, font_size)

    draw_text_in_list(legend_draw, font, FONT_COLOR, sub_box_b2.get_dimensions(), text, padding)


    # Append symbol in b3.
    # Open the image.
    image_path = government_dict.get('symbol_path')
    with Image.open(image_path) as symbol_image:
        # Resize image. (take padding into consideration)
        width, height = b3.get_width_height()
        width = int(width-(2*padding))
        height = int(height-(2*padding))
        symbol_image = symbol_image.resize((width, height))

        # Paste image to the legend image. (image, coordinates, mask)
        x, y = b3.start
        x += padding
        y += padding
        legend_image.paste(symbol_image, (x, y), symbol_image)

    # Append law level in b4
    # Create the image
    image_path = "Images/sheriff-badge.png"
    with Image.open(image_path) as law_image:
        # Get image size
        im_width, im_height = law_image.size

        # Create font
        font_size = int(im_height / 4)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Get law level to write
        law_level = str(upp_dict.get('law_level'))

        # Check font width, height.
        font_width, font_height = get_text_dimensions(law_level, font)

        # Get coordinate for the text.
        x = int((im_width - font_width)/2)
        y = int(((im_height - font_height)/2) + im_height/35)

        # Draw the text at coordinates
        law_draw = ImageDraw.Draw(law_image)
        law_draw.text((x, y), law_level, FONT_COLOR, font)
        law_image = law_image.resize(b4.get_width_height())

        # Append to legend image.
        legend_image.paste(law_image, b4.start, law_image)


    # Append tech level in b5
    # Create the image
    image_path = "Images/circuit.png"
    with Image.open(image_path) as law_image:
        # Get image size
        im_width, im_height = law_image.size

        # Create font
        font_size = int(im_height / 4)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Get tech level to write
        law_level = str(upp_dict.get('tech_level'))

        # Check font width, height.
        font_width, font_height = get_text_dimensions(law_level, font)

        # Get coordinate for the text.
        x = int(((im_width - font_width)/2) - im_width/80)
        y = int(((im_height - font_height)/2) - im_height/50)

        # Draw the text at coordinates
        law_draw = ImageDraw.Draw(law_image)
        law_draw.text((x, y), law_level, FONT_COLOR, font)
        law_image = law_image.resize(b5.get_width_height())

        # Append to legend image.
        legend_image.paste(law_image, b5.start, law_image)

    return legend_image


def generate_faction_name():
    """Generates a faction name randomly using lists of adjective,
    adverbs, nouns and verbs

    Returns:
        string: A text string representing a faction name
    """
    # Import the json-data
    with open("Data/nouns.json",) as nouns_json:
        nouns_list = json.load(nouns_json)

    with open("Data/verbs.json",) as verbs_json:
        verbs_list = json.load(verbs_json)

    with open("Data/adverbs.json",) as adverbs_json:
        adverbs_list = json.load(adverbs_json)
    
    with open("Data/adjectives.json",) as adjectives_json:
        adjectives_list = json.load(adjectives_json)

    # Generate random adjective, adverbs, nouns and verbs
    adjective = random_choice(adjectives_list)
    adverb = random_choice(adverbs_list)
    noun = random_choice(nouns_list)
    noun2 = random_choice(nouns_list)
    verb = random_choice(verbs_list)


    generated_name_list =[
        f'{adjective} {noun}',
        f'{adverb} {verb} of the {adjective} {noun}',
        f'The {verb} {noun}',
        f'The {verb} {noun}s',
        f'{verb} {noun} of {adjective} {noun2}s'
    ]

    return random_choice(generated_name_list)


def generate_factions(upp_dict : dict) -> dict:
    """Takes UPP data and returns randomly generated factions.

    Args:
        upp_dict (dict): UPP data in dictionary form.

    Returns:
        dict: Includes a dictionary for each faction. Faction name being the keys for the
        subdictionaries.
    """
    # Create an empty dict to hold the values
    faction_dict = {}

    # Determine how many factions should be generated
    # Formula roll a D3 add +1 if government type is 0 or 7
    number_of_factions = randint(1, 3)
    government_type = upp_dict.get('government_type')

    if government_type == 0 or government_type == 7:
        number_of_factions += 1

    # Load in the cultural differences.
    with open("Data/cultural_differences_data.json",) as cultures_json:
        culture_dict = json.load(cultures_json)

    # Iterate and create each faction.
    for _ in range(number_of_factions):
        faction = {}
        # Get faction name
        faction_name = generate_faction_name()

        # Update to faction
        faction.update({'name' : faction_name})
        
        # Get Faction support level
        support_level = ""
        result = roll_2d()

        if 0 < result <= 3:
            support_level = 'Obscure group'
        elif 4 <= result <= 5:
            support_level = "Fringe group"
        elif 6 <= result <= 7:
            support_level = "Minor group"
        elif 8 <= result <= 9:
            support_level = "Notable group"
        elif 10 <= result <= 11:
            support_level = "Significant group"
        elif result == 12:
            support_level = "Overwhelming support"

        # Update faction with support level.
        faction.update({'support' : support_level})

        # Get cultural differences/traits
        # Roll D66 for result
        dice_roll = roll_d66()

        # Create empty string variable.
        culture_type = ""

        # If 25  Generate with fstring f'Influenced - {reroll]'
        if dice_roll == 25:
            # Reroll until the result is not uniqe case 25 or 26
            while dice_roll in [25, 26]:
                dice_roll = roll_d66()
            culture = culture_dict.get(str(dice_roll)).get('type')

            culture_type = f'Influenced - {culture}'

        # If 26 Generate with a fstring f'Fusion of {reroll1} & {reroll2}
        elif dice_roll == 26:
            # Roll both dice
            dice_1 = roll_d66()
            dice_2 = roll_d66()

            # Reroll dice1 until the result is not uniqe case 25 or 26
            while dice_1 in [25, 26]:
                dice_1 = roll_d66()

            # Reroll dice2 until its not uniqe case 25, 26 or the same as dice1
            while dice_2 in [25, 26, dice_1]:
                dice_2 = roll_d66()

            # Save the two dictionaries from culture_dict
            culture_1 = culture_dict.get(str(dice_1)).get('type')
            culture_2 = culture_dict.get(str(dice_2)).get('type')
            culture_type = f'Fusion of {culture_1} & {culture_2}'

        else:
            culture_type = culture_dict.get(str(dice_roll)).get('type')

        # Append culture to faction.
        faction.update({'culture' : culture_type})

        # Append to faction_dict
        faction_dict.update({faction_name : faction})


    return faction_dict


def legend_append_factions(legend_image, upp_dict):
    """Appends faction information to an image using data from a upp_dict.

    Args:
        legend_image (PIL.Image): Image to append the data to.
        upp_dict (dict): dictionary containing UPP-Serial data.

    Returns:
        PIL.Image: Image with the appended faction text.
    """
    # ------------------------------------------------------------------------
    # |b1                                |b2                |b3              |
    # |                                  |                  |                |
    # |                                  |                  |                |
    # |                                  |                  |                |
    # |                                  |                  |                |
    # |                                  |                  |                |
    # |                                  |                  |                |
    # ------------------------------------------------------------------------
    # b1 : all faction names
    # b2 : all faction support levels
    # b3 : all faction cultures

    # Calculate box sizes
    im_width, _ = legend_image.size
    width = int(2 * im_width / 3)
    box_height = int(im_width/4)

    x_offset = 0
    y_offset = int(width / 2)


    # Bound box b1
    b1_percent = 52
    b1_width = int(percent_of_number(width, b1_percent))

    b1 = BoundBox(x_offset, y_offset, x_offset + b1_width, y_offset + box_height)

    # Bound box b2
    x_offset += b1_width

    b2_percent = 28
    b2_width = int(percent_of_number(width, b2_percent))

    b2 = BoundBox(x_offset, y_offset, x_offset + b2_width, y_offset + box_height)

    # Bound box b3
    x_offset += b2_width

    b3_percent = int(100 - (b1_percent + b2_percent))
    b3_width = int(percent_of_number(width, b3_percent))

    b3 = BoundBox(x_offset, y_offset, x_offset + b3_width, y_offset + box_height)


    # Create the draw class.
    legend_draw = ImageDraw.Draw(legend_image)

    # Font data.
    padding = 20


    # Get a dictionary of factions
    factions_dictionary = generate_factions(upp_dict)
    
    # Create the lists to be written in subboxes
    faction_names = [f'Faction:']
    faction_support_levels = [f'Support:']
    faction_cultures = [f'Culture:']

    for name, faction_data in factions_dictionary.items():
        faction_names.append(name)
        faction_support_levels.append(faction_data.get('support'))
        faction_cultures.append(faction_data.get('culture'))


    # Create sub boxes for each field.
    # Sub box for faction names.
    x1, y1 = b1.start
    x2, _ = b1.end
    y2 = int((b1.get_height() / len(faction_names)) + y1)

    sub_box_b1 = BoundBox(x1, y1, x2, y2)

    # Sub box for faction support.
    x1, y1 = b2.start
    x2, _ = b2.end
    y2 = int((b2.get_height() / len(faction_support_levels)) + y1)

    sub_box_b2 = BoundBox(x1, y1, x2, y2)

    # Sub box for faction names.
    x1, y1 = b3.start
    x2, _ = b3.end
    y2 = int((b3.get_height() / len(faction_cultures)) + y1)

    sub_box_b3 = BoundBox(x1, y1, x2, y2)


    # Find maximum font size for faction names
    font_size = get_max_font_size_from_list(faction_names,
                                            FONT_PATH,
                                            sub_box_b1.get_dimensions(),
                                            padding)

    # Make a separate font for faction names.
    name_font = ImageFont.truetype(FONT_PATH, font_size)

    # Compare to the maximum font size of support levels.
    font_size_temp = get_max_font_size_from_list(faction_support_levels,
                                            FONT_PATH,
                                            sub_box_b2.get_dimensions(),
                                            padding)

    # Use the smallest font size.
    if font_size_temp < font_size:
        font_size = font_size_temp

    # Compare to the maximum font size of support levels
    font_size_temp = get_max_font_size_from_list(faction_cultures,
                                            FONT_PATH,
                                            sub_box_b3.get_dimensions(),
                                            padding)

    # Use the smallest font size.
    if font_size_temp < font_size:
        font_size = font_size_temp

    # Create the font.
    font = ImageFont.truetype(FONT_PATH, font_size)

    # Write names as list.
    draw_text_in_list( legend_draw,
                        name_font,
                        FONT_COLOR,
                        sub_box_b1.get_dimensions(),
                        faction_names,
                        padding)

    # Write support as list.
    draw_text_in_list( legend_draw,
                        font,
                        FONT_COLOR,
                        sub_box_b2.get_dimensions(),
                        faction_support_levels,
                        padding)

    # Write culture as list.
    draw_text_in_list( legend_draw,
                        font,
                        FONT_COLOR,
                        sub_box_b3.get_dimensions(),
                        faction_cultures,
                        padding)

    # Draw a separating line from headers and data.
    line_width = 4

    x1 = sub_box_b1.get_side('left')
    x2, y = sub_box_b3.end

    legend_draw.line([(x1, y), (x2, y)], LINE_COLOR, line_width)

    # Draw thin lines separating every subbox.
    sub_box_height = sub_box_b1.get_height()
    for line_offset_multiplier in range(len(faction_names) - 1):
        offset = (line_offset_multiplier * sub_box_height)

        legend_draw.line([(x1, y + offset), (x2, y + offset)], LINE_COLOR, int(line_width / 2))


    return legend_image


def legend_append_contraband_lists(legend_image, upp_dict):
    """Takes an image to append contraband data to using the UPP

    Args:
        legend_image (PIL.Image): Image to append the data to.
        upp_dict (dict): Dictionary containing all the UPP-Data.

    Returns:
        PIL.Image: Returns the image with appended data.
    """

    # Draw ascii art depicting the subboxes and what goes where.
    #------------------------------------------------------------
    #| Law level |      b1      |      b2       |      bn       |
    #------------------------------------------------------------
    #|    1      |              |               |               |
    #|           |              |               |               |
    #------------------------------------------------------------
    #|    2      |              |               |               |
    #|           |              |               |               |
    #------------------------------------------------------------
    #|    3      |              |               |               |
    #|           |              |               |               |
    #------------------------------------------------------------
    #|    ...    |              |               |               |
    #|           |              |               |               |
    #------------------------------------------------------------
    #|     9     |              |               |               |
    #|           |              |               |               |
    #------------------------------------------------------------
    # Make a law level number for each law level the planet.
    # has contraband for. (Set the width of this column to a percent)
    #
    # Make a row b1-b2 for every contraband type on the planet.
    # The contraband boxes share the remaining space equally.
    

    # Create ImageDraw.Draw class for appendinglines and text.
    legend_draw = ImageDraw.Draw(legend_image)

    # Set local font properties.
    # Font data.
    padding = 10


    # Fetch contraband dictionary with contraband for each law level.
    with open("Data/contraband_data.json",) as contraband_json:
        contraband_dictionaries = json.load(contraband_json)

    
    # Determine what the planet considers contraband.
    government_type = str(upp_dict.get('government_type'))
    with open("Data/government_data.json",) as government_data_json:
        contraband = json.load(government_data_json).get(government_type).get('contraband')


    # If Weapon is considered contraband. Also add Armour
    if "Weapons" in contraband:
        contraband.append("Armour")
    

    # Determine what levels has entires.
    law_levels_with_entries = []
    law_level = upp_dict.get('law_level')

    for level in range(1, law_level):
        for category in contraband:
            # Handle if contraband is 'Varies'.
            if category == 'Varies':
                law_levels_with_entries.append(str(level))
                break
            # Handle if contraband is 'None'
            if category == 'None':
                break
            contraband_dictionary = contraband_dictionaries.get(category)
            if str(level) in contraband_dictionary.keys():
                law_levels_with_entries.append(str(level))
                break


    # Create a list containing the titles.
    titles = ['Law']
    for name in contraband:
        titles.append(name)

    
    # Calculate BoundBoxes.
    # Weapons, Armour, Information, Technology, Travelers, Psionics
    im_width, im_height = legend_image.size
    x1, y1 = 0 , int((7 * im_width) / 12)
    x2, y2 = int(im_width / 2), im_height

    # Main box.
    main_box = BoundBox(x1, y1, x2, y2)


    # If there is no law (law = 0) write a special message
    if len(law_levels_with_entries) == 0:
        warning_message = """
            The only law you will find on this rock, is\n
            the law you and your companions make with your\n
            own firepower, contacts and wits.\n\n
            It is highly recommended you carry a firearm\n
            and your finest piece of armor."""
        
        font_size = get_multiline_max_font_size(main_box.get_dimensions(),
                                                warning_message, FONT_PATH, padding)

        draw_text_bound_box(main_box, warning_message, FONT_PATH,
                            legend_draw, FONT_COLOR, padding,
                            vertical_alignment='center', horizontal_alignment='center')
        return legend_image
    

    # Create a title height and law width.
    law_box_width_percentage = 14
    law_box_width = percent_of_number(main_box.get_width(), law_box_width_percentage)

    # Get the title height.
    title_box_height_percentage = 10
    title_box_height = percent_of_number(main_box.get_height(), title_box_height_percentage)

    # Create special law box case
    law_box = BoundBox(x1, y1, (x1 + law_box_width), (y1 + title_box_height))

    # Create a law bound box array.
    law_main_box = BoundBox(x1, (y1 + title_box_height), law_box_width, y2)

    # Create a title bound box array
    title_main_box = BoundBox((x1 + law_box_width), y1, x2, (y1 + title_box_height))

    # Contraband elements box
    contraband_main_box = BoundBox((x1 + law_box_width), (y1 + title_box_height), x2, y2)


    # Split them into subboxes.
    law_sub_boxes = law_main_box.split(horizontal_splits=(len(law_levels_with_entries)))

    # Get the remaining title sub boxes minus the one for "law"
    title_sub_boxes = title_main_box.split(vertical_splits=(len(titles) - 1))

    # Append the titles after the special size law_box (remember the sub box array is a 2D array)
    title_temp_array = [[law_box]]
    for array in title_sub_boxes:
        title_temp_array.append(array)

    title_sub_boxes = title_temp_array

    # Contraband sub_boxes
    contraband_sub_boxes = contraband_main_box.split(vertical_splits=len(contraband),
                                                    horizontal_splits=len(law_levels_with_entries))


    # Get maximum font size allowed for title and law level numbers.
    col, row = 0, 0

    # All subboxes are of the same size. Grabbing the first element to determine font size.
    font_size = get_max_font_size_from_list(law_levels_with_entries, FONT_PATH,
                                            law_sub_boxes[col][row].get_dimensions())

    # Adjust the font size to only part of the box
    font_size = int(font_size / 3)

    # Write every law level number in the subboxes.
    # Sub box array in 2D array format. Grabbing the first (and only column)
    for sub_box, law_level in zip(law_sub_boxes[col], law_levels_with_entries):
        draw_text_bound_box(sub_box, law_level, FONT_PATH, legend_draw,
                            FONT_COLOR, font_size=font_size,
                            vertical_alignment='top', horizontal_alignment='center')


    # TODO: Ensure the font sizes works. Right now Law is not determined inside its
    # own box.
    # Get max font size for the titles.
    font_size = get_max_font_size_from_list(titles, FONT_PATH,
                                                title_sub_boxes[col + 1][row].get_dimensions())


    # Write every title in the subboxes.
    # Sub box array in 2D array format. Grabbing the first row value in every col.
    for sub_box, title in zip(title_sub_boxes, titles):
        draw_text_bound_box(sub_box[row], title, FONT_PATH, legend_draw,
                            FONT_COLOR, font_size=font_size,
                            vertical_alignment='center', horizontal_alignment='center')


    # Find max font size for the contraband boxes

    # Set initial font_size and get any sub_box from contraband sub boxes since they are all of the
    # same size.
    font_size = 0
    sub_box = contraband_sub_boxes[0][0]
    for law_level in law_levels_with_entries:
        for category in contraband:
            # Handle if category is 'Varies'.
            if category == 'Varies':
                break
            contraband_dictionary = contraband_dictionaries.get(category)
            if law_level in contraband_dictionary.keys():
                # Get text from array.
                text_array = contraband_dictionary.get(law_level)

                # Convert it into a multiline string.
                text = '\n'.join(text_array)

                # Get font size.
                temp_font_size = get_multiline_max_font_size(sub_box.get_dimensions(),
                                text, FONT_PATH, padding)

                if font_size == 0 or temp_font_size < font_size:
                    font_size = temp_font_size

    
    # Write the contraband data in subboxes
    for sub_box_column, category in zip(contraband_sub_boxes, contraband):
        # Handle if category is 'Varies'.
        if category == 'Varies':
            break
        # Get dictionary for the column.
        contraband_dictionary = contraband_dictionaries.get(category)

        # Step through each row.
        for sub_box, law_level in zip(sub_box_column, law_levels_with_entries):
            if law_level in contraband_dictionary.keys():
                # Get text array from dictionary.
                text_array = contraband_dictionary.get(law_level)

                # Convert to multiline string.
                text = '\n'.join(text_array)

                # Draw the text
                draw_text_bound_box(sub_box, text, FONT_PATH,
                                    legend_draw, FONT_COLOR, padding, font_size=font_size)


    # Local line data for separating the different subboxes.
    line_width = 2

    # Get sub box height. (All sub boxes has the same height.)
    box_height = contraband_sub_boxes[0][0].get_height()

    # Draw from x1 to x2 at the top of every box.
    y_offset = y1 + title_box_height
    for line_num in range(len(contraband_sub_boxes[0])):
        y = y_offset + (line_num * box_height)
        legend_draw.line((x1, y, x2, y), LINE_COLOR, line_width)


    return legend_image


def generate_legend(upp_dict, color_palette, path, planet_name, debug = False):
    """Generates a planetary legend to give better overview for players.

    Args:
        upp_dict (dict): an UPP dictionary containing all generated planetary aspects.
        color_palette (dict): A dictionary containing the colors and color names used
        in painting the world (E.g. grass : "turtle_green")
        path (str): string providing the folder where the planetary image has been saved.
        planet_name (str): name of the planet. Used to ensure the legends
        name will be <planet name>_legend
    """
    # Make sure the path directory exist. Otherwise create it.
    if not os.path.exists(path):
        os.makedirs(path)

    # Generate legend layout document as an Image.
    legend_doc = generate_legend_document()

    # Determine trade codes and add to legend document.
    trade_codes = determine_trade_codes(upp_dict)

    # Append trade information to bottom right of the legend document.
    legend_doc = legend_append_trade_codes(legend_doc, trade_codes)

    # Append gravity and diamater data to the top middle of the legend document
    # Atmospherics, Temperature, day/night cycle.
    legend_doc = legend_append_planetary_metrics(legend_doc, upp_dict)

    # Append planetary image to the top right of the legend document
    planet_image_path = os.path.join(path, planet_name + '.png')
    legend_doc = legend_append_planetary_image(legend_doc, planet_image_path)

    # Append a color to landmass type underneath the planetary image.
    legend_doc = legend_append_color_legend(legend_doc, color_palette)

    # Append planet name, UPP-Serial and government type to the top left of the legend document.
    legend_doc = legend_append_name_government_data(legend_doc, planet_name, upp_dict)

    # Generate factions and add cultures.
    legend_doc = legend_append_factions(legend_doc, upp_dict)

    # Determine contraband and append them to the bottom left under separate categories.
    legend_doc = legend_append_contraband_lists(legend_doc, upp_dict)


    if debug:
        legend_doc.show()
    else:
        # Create path to save location
        planet_name += '_legend.png'
        path = os.path.join(path, planet_name)

        # Save image to path with <name>_legend as PNG.
        legend_doc.save(path, 'PNG')


def main():
    # If called directly. Make planetary data up
    # and display the image.
    debug = True
    upp_dict = upp_to_dict('A344556-10')
    color_palette = create_color_palette(upp_dict)
    path = os.path.join(os.getcwd(), 'Saved')
    planet_name = 'Debug'

    generate_legend(upp_dict, color_palette, path, planet_name, debug)


if __name__ == '__main__':
    main()