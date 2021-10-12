# Takes an UPP dictionary (Universal planetary profile) and cretes a map legend
# This include descriptive name of the different colors, goverment type, temperature range,
# Atmosphearic demands, Startport quality and trade codes.
import json
from planet_generator import create_color_palette
from planet_generator import upp_to_dict

def generate(upp_dict, color_palette):
    #TODO: Gather necessary information
    #TODO: Create 
    pass


def determine_trade_codes(upp_dict):
    with open("trade_code_classification.json",) as trade_requirement_data:
        trade_requirements = json.load(trade_requirement_data)
    #TODO: Start checking wich codes apply.


def make_legend(upp_dict, color_palette, path):
    pass
    #TODO: Create the legend
    #TODO: Determine trade codes
    #TODO: Save to path with <name>_legend


def main():
    upp_dict = upp_to_dict('3344556-10')
    color_palette = create_color_palette(upp_dict)


if __name__ == '__main__':
    main()