"""
This module contains accessory code for use in the other database modules.
"""

from util import prompts

def add_attribute_loop(add_dict=None):
    """
    Collects multiple key,value pairs to update a record object. As many
    such pairs as desired can be added before quitting.
    """
    if add_dict is None:
        add_dict = {}
    loop = True
    while loop is True:
        attr = prompts.StringPrompt(
            message = 'Please specify an attribute to add').prompt()
        value = prompts.StringPrompt(
            message = 'Please specify a value for {}'.format(attr)).prompt()
        user_conf = prompts.YesNoPrompt(
            message = 'You have entered {} {}, is this correct?'.format(
                attr,value)).prompt()
        if user_conf.lower() in {'yes','y'}:
            add_dict[attr] = value
        elif user_conf.lower() in {'no','n'}:
            print('Attribute {} will not be added'.format(attr))
        cont = prompts.YesNoPrompt(
            message = 'Do you wish to add more attributes?').prompt()
        if cont.lower() in {'yes','y'}:
            pass # keep looping
        elif cont.lower() in {'no','n'}:
            loop = False
    return add_dict
