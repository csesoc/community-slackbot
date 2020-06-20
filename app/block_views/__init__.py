from pathlib import Path
import json

TEST_VIEW_ONE = "test"
__CACHED_VIEWS = {}


def try_load_view(view):
    """
    Attempts to load block kit view directly from file
    :param view: The name of the file to view e.g "onboarding.json"
    :return: JSON String representation of block view if it exists else None
    """
    view_path = Path("app/block_views/") / view
    try:
        return view_path.read_text()
    except FileNotFoundError:
        return None


def get_block_view(view):
    """
    Gets a block kit view from the given identifier name
    :param view: Block kit view identifier name
    :return: JSON String representation of block view
    """
    if view in __CACHED_VIEWS:
        return __CACHED_VIEWS[view]

    loaded_view = try_load_view(view)
    if loaded_view is not None:
        __CACHED_VIEWS[view] = loaded_view
    return loaded_view


# Functions to load block_views start here
# Block_views may vary from block_view to block_view,
# so each one is tailored to the situation.
def onboarding(user_id):
    """
    Retrieve a personalised block view of the onboarding message
    :param user: A string of 9 characters representing a slack user id
    :return: Array of json objects representing the blocks for slack
    """
    view = get_block_view("onboarding.json").replace("%%USER%%", f"<@{user_id}>")
    return json.loads(view)["blocks"]


def edit_profile(current):
    """
    Retrieve the "edit_profile" modal, and fill in the specfied initial values.
    :current: A dictionary of key-value pairs corresponding to the user's current profile details.
    :return: A json object which represents the view of the "edit_profile" modal with correct intial values.
    """
    # Retrieve raw "edit_profile" modal view
    string_view = get_block_view("edit_profile.json")

    # Insert intial values into the respective fields, and clearing any that the user has not yet set.
    for key in ["favourite_course", "favourite_programming_language", "favourite_netflix_show", "favourite_food", \
            "overrated", "underrated", "biggest_flex", "enrolled_courses", "completed_courses", "general_interests"]:
        try:
            string_view = string_view.replace(f"%%{key}%%", current[key])
        except KeyError:
            string_view = string_view.replace(f"%%{key}%%", "")

    # Return intialised json view
    return json.loads(string_view)


def commands_help():
    """
    Retrieve the "commands_help" modal.
    :return: A json object which represents the view of the "commands_help" modal.
    """
    return json.loads(get_block_view("commands_help.json"))
