# Takes an UPP dictionary (Universal planetary profile) and cretes a map legend
# This include descriptive name of the different colors, goverment type, temperature range,
# Atmosphearic demands, Startport quality and trade codes.
import json
import os
import colors
from planet_generator import create_color_palette
from planet_generator import upp_to_dict

def generate(upp_dict, color_palette):
    #TODO: Gather necessary information
    #TODO: Create 
    pass


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


def make_legend(upp_dict, color_palette, path, planet_name):
    # Make sure the path directory exist. Otherwise create it.
    if not os.path.exists(path):
        os.makedirs(path)

    # Determine trade codes
    trade_codes = determine_trade_codes(upp_dict)
    print(trade_codes)

    #TODO: Create the legend

    #TODO: Save to path with <name>_legend.
    planet_name += '_legend'
    path = os.path.join(path, planet_name)



def main():
    upp_dict = upp_to_dict('3344556-10')
    color_palette = create_color_palette(upp_dict)
    path = os.path.join(os.getcwd(), 'Saved')
    planet_name = 'Debug'

    make_legend(upp_dict, color_palette, path, planet_name)


if __name__ == '__main__':
    main()