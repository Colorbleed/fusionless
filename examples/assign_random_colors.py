import fusionscript as fu
import random

def get_random_color():
    clr = {}
    for key in ['R', 'G', 'B']:
        clr[key] = random.uniform(0, 1)
    return clr

def process():
    c = fu.Comp()
    for tool in c.get_selected_tools():
        tool.set_tile_color(get_random_color())
        tool.set_text_color(get_random_color())