"""
Interface for Goat-style searches. Users can choose to perform searches,
analyze previous searches, collate data to produce output, and likely a
list of other features as well - such as getting output sequence files
for use in other analyses?
"""

from util.inputs import prompts
from searches import search_config

valid_options = {'search', 'results', 'summary', 'analysis', 'quit'}

def search_loop():
    """Performs/analyzes searches based on user input"""
    loop = True
    while loop == True:
        user_input = prompts.LimitedPrompt(
            message = 'Please choose (search, results, summary, analysis, quit)',
            errormsg = 'Unrecognized action',
            valids = valid_options).prompt()
        if user_input == 'search':
            search_config.new_search()
        elif user_input == 'results':
            search_config.get_search_results()
        elif user_input == 'summary':
            search_config.summarize_search_results()
        elif user_input == 'analysis':
            search_config.new_analysis()
        elif user_input == 'quit':
            loop = False
