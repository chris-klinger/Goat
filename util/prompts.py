"""
Contains a class-style interface for prompts used throughout Goat.
"""

import re

class Prompt:
    """
    Superclass from which all subclasses should be derived for specific
    prompts. Subclass must implement validate() method.
    """
    def __init__(self, message=None, errormsg=None, valids=None):
        self.message = message
        self.errormsg = errormsg
        self.valids = valids
    def prompt(self):
        """Prompts a user for input"""
        user_input = None
        while user_input is None:
            user_input = input(str(self.message)+' => ')
            if not self.validate(user_input):
                print(str(self.errormsg))
                user_input = None
        return user_input
    def validate(self, user_input):
        """Must be implemented in subclass!"""
        raise NotImplementedError("please use subclass")

class StringPrompt(Prompt):
    """Prompts user input, expects a string in return"""
    def validate(self, user_input):
        return True  # user input is always in a string

class LimitedPrompt(Prompt):
    """Checks input against a subset of possibilites"""
    def validate(self, user_input):
        if user_input in self.valids:
            return True
        return False

class YesNoPrompt(Prompt):
    """Checks whether user input is a valid yes/no response"""
    def __init__(self, message=None, errormsg=None, valids=None):
        if errormsg is None:
            errormsg = 'Please enter YES/yes/Y/y or NO/no/N/n'
        Prompt.__init__(self, message, errormsg, valids)
    def validate(self, user_input):
        if user_input.lower() in {'yes', 'no', 'y', 'n'}:
            return True
        return False

class RecordPrompt(Prompt):
    """Looks for input like <\w+>_<\w+>"""
    def __init__(self, message=None, errormsg=None, valids=None):
        if errormsg is None:
            errormsg = 'Input does not appear to be a valid record'
        Prompt.__init__(self, message, errormsg, valids)
    def validate(self, user_input):
        record_pattern = re.compile(r'\w+_\w+')
        if record_pattern.search(user_input):
            return True
        return False

class FilePrompt(Prompt):
    """Prompts user input of a file"""
    def validate(self, user_input):
        """Checks for a valid file"""
        import os
        if os.path.isfile(user_input):
            return True
        return False

class DirPrompt(Prompt):
    """Prompts user input of a directory"""
    def validate(self, user_input):
        import os
        if os.path.isdir(user_input):
            return True
        return False
