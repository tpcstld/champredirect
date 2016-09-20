import os
from flask import Flask
from flask import redirect

app = Flask(__name__)

# Constants for generating redirects.
CHAMPION_GG_BASE_URL = "//champion.gg"
CHAMPION_GG_CHAMPION_URL_SUBPATH = "/champion/"
REDIRECT_CODE = 302

# Constants for retrieving champion and role mapping.
CHAMPION_MAPPING_FILE_NAME = "championmaps.txt"

ROLE_WORDS = {
    "Top": ["top"],
    "Jungle": ["jungle", "jg"],
    "Middle": ["middle"],
    "ADC": ["adc", "bottom"],
    "Support": ["support"],
}

# To be generated.
CHAMPION_MAPPING = {}
ROLE_MAPPING = {}


def on_startup():
    """Executed when the service is started.
    Populates the champion and role mappings.
    """
    global CHAMPION_MAPPING
    global ROLE_MAPPING

    # Generate champion mapping from file
    champion_mapping_file_path = os.path.join(
            os.getcwd(), CHAMPION_MAPPING_FILE_NAME)

    with open(champion_mapping_file_path, "r") as mapping_data:
        for line in mapping_data:
            alias, champion = line.split()
            CHAMPION_MAPPING[alias] = champion

    for role_name in ROLE_WORDS:
        words = ROLE_WORDS[role_name]
        for word in words:
            # For user convenience, we also want every prefix of a whole
            # term to refer to the same term.
            for x in range(1, len(word) + 1):
                ROLE_MAPPING[word[:x]] = role_name

on_startup()

@app.route('/')
def index():
    """Navigates to champion.gg
    """
    return redirect(CHAMPION_GG_BASE_URL, code=REDIRECT_CODE)

def find_champion_name(data):
    """Takes in a string data and tries to find the name of the champion that
    the string is referring to.

    Returns None if there is no good match.
    """
    data = data.lower()
    if data not in CHAMPION_MAPPING:
        return None

    return CHAMPION_MAPPING[data]

def find_role_name(data):
    """Takes in a string data and tries to find the name of the role that the
    string is referring to.

    Returns None if there is no good match.
    """
    data = data.lower()
    if data not in ROLE_MAPPING:
        return None

    return ROLE_MAPPING[data]

@app.route('/<path:path>')
def search(path):
    """Navigates to a specific champion on champion.gg

    The path string should be specified as:
        champion/role
    """
    sections = path.split("/")

    champion_input = sections[0]
    role_input = None
    if len(sections) > 1:
        role_input = sections[1]

    champion_name = find_champion_name(champion_input)
    role_name = None
    if role_input:
        role_name = find_role_name(role_input)

    # Just plug in the name directly.
    if not champion_name:
        champion_name = champion_input.lower()

    result_url = \
        CHAMPION_GG_BASE_URL + CHAMPION_GG_CHAMPION_URL_SUBPATH + champion_name

    if role_name:
        result_url = result_url + "/" + role_name

    return redirect(result_url, code=302)


if __name__ == '__main__':
    app.run()
