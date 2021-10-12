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
    """Takes a Universal planetary profile dictionary and returns a list of which trade codes
    they qualify for

    Args:
        upp_dict (Dict): Dictionary containing upp data.

    Returns:
        [List]: Returns a list of all trade codes the planet qualify for.
    """
    # Load the trade code determinants from JSON.
    with open("trade_code_classification.json",) as trade_requirement_data:
        trade_requirements = json.load(trade_requirement_data)

    categorization = []
    # Start checking wich codes apply going through each element in the json data.
    for _, type_requirements in trade_requirements.items():

        trade_code_requirement_met = True
        for key, requirement in type_requirements.items():
            if not key == 'code' and not requirement == None:
                if requirement[0] == 'range':
                    min, max = requirement[1], requirement[2]
                    if not value_in_range(upp_dict.get(key), min, max):
                        trade_code_requirement_met = False
                        break
                elif requirement[0] == 'specific':
                    if upp_dict.get(key) not in requirement[1]:
                        trade_code_requirement_met = False
                        break
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
    #print(trade_codes)

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