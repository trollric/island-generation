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
    line_width = 15

    # Draw the legnd boundary lines.
    legend_draw.rectangle([(0, 0), (legend_width, legend_height)],
                                    outline=line_fill_color,
                                    fill=background,
                                    width=line_width)
    
    # Draw first three boxes
    box_x = int(legend_width/3)
    box_y = box_x
    div1 = [(box_x, 0), (box_x, box_y)]
    div2 = [(box_x*2, 0), (box_x*2, box_y)]
    sep1 = [(0, box_y),(box_x*3, box_y)]
    lines = [div1, div2, sep1]

    for line in lines:
        legend_draw.line(line, fill=line_fill_color, width=line_width)

    return legend_im

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

    # TODO: Generate legend layout document as an Image.
    legend_doc = generate_legend_document()
    legend_doc.show()
    # Determine trade codes and add to legend document.
    trade_codes = determine_trade_codes(upp_dict)
    # TODO: Append trade information to bottom right of the legend document.

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

    # Save to path with <name>_legend.
    # Create path
    planet_name += '_legend'
    path = os.path.join(path, planet_name)

    # TODO: Save the image.


def main():
    # If called directly. Make planetary data up.
    upp_dict = upp_to_dict('A344556-10')
    color_palette = create_color_palette(upp_dict)
    path = os.path.join(os.getcwd(), 'Saved')
    planet_name = 'Debug'

    generate_legend(upp_dict, color_palette, path, planet_name)


if __name__ == '__main__':
    main()