import os
import json

from app.models import Courses

TEST_VIEW_ONE = "test"
__CACHED_VIEWS = {}


def try_load_view(view):
    """
    Attempts to load block kit view directly from file
    :param view:
    :return:
    """
    view_path = os.path.join("app/block_views", view)
    if os.path.exists(view_path):
        return open(view_path, "r").read()
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


def get_report_modal(message_id):
    return get_block_view("views/anonymous/report_message.json")\
        .replace("{MESSAGE_ID}", str(message_id))


def get_anonymous_modal():
    return get_block_view("views/anonymous/anonymous_messaging_modal.json")


def get_anonymous_reply_modal(message_id):
    return get_block_view("views/anonymous/anonymous_messaging_modal_reply.json")\
        .replace("{MESSAGE_ID}", str(message_id))


def get_anonymous_message(message, message_id):
    return get_block_view("views/anonymous/anonymous_message.json")\
        .replace("{ANONYMOUS_MESSAGE}", message)\
        .replace("{MESSAGE_ID}", str(message_id))


def get_course_select_outline():
    courses = [c.course for c in Courses.query.order_by(Courses.course.asc()).all()]
    items = []
    for course in courses:
        item = """{
        "text": {
            "type": "plain_text",
            "text": "{course}",
            "emoji": true
        },
        "value": "value-0"
    }""".replace("{course}", course)
        items.append(item)
    return get_block_view("views/courses/select_course_outline.json").replace("{COURSES_OPTIONS}", ",".join(items))

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


def job_block(job):
    """
    Retrieves the job block, and populates it with the required information.
    :param job: A dictionary with 4 fields: link, title, company, location.
    :return: A job block with the respective fields.
    """

    # Retrieve raw "job_block" block
    block = get_block_view("job_block.json")

    # Insert data into the block
    block = block.replace("%%LINK%%", job["link"])
    block = block.replace("%%TITLE%%", job["title"])
    block = block.replace("%%COMPANY%%", job["company"])
    block = block.replace("%%LOCATION%%", job["location"])

    # Return the block as a dictionary
    return json.loads(block)


def job_opportunities(query, text, jobs):
    """
    Retrieves the job_opportunities view, and populates it with the required information.
    :param query: The query string that the user uses to search.
    :param text: The status of the search.
    :param jobs: An array of dictionaries with 4 fields: link, title, company, location.
    :return: A job oppotunities view with the respective fields populated.
    """

    # Retrieve raw "job_opportunitites" view
    view = get_block_view("job_opportunities.json")

    # Insert query and text into the views
    view = view.replace("%%QUERY%%", query)
    view = view.replace("%%TEXT%%", text)

    # Transform the string into a dictionary
    view = json.loads(view)
    blocks = view["blocks"]

    # Add each job to the view after formatting it
    for job in jobs:

        # Format the jobs
        formatted_job = job_block(job)

        # Insert the block into the second last position of the array
        blocks.insert(-1, formatted_job)

    # Return the view
    return view


def permission_denied():
    """
    Retrieve the "generic_permission_denied" modal.
    :return: A json object which represents the view of the "generic_permission_denied" modal.
    """
    return json.loads(get_block_view("generic_permission_denied.json"))


def error_message(message):
    """
    Retrieve the "error_message" modal.
    :param message: A string which represents the error message
    :return: A json object which represents the view of the "error_message" modal.
    """
    modal = get_block_view("error_message.json").replace("%%ERROR_MESSAGE%%", message)
    return json.loads(modal)


def purge_confirmation(number_of_messages, user, time_period, channel_id, text_snippet):
    """
    Retrieve the "purge_confirmation" modal.
    :param number_of_messages: Integer which represents the number of messages to delete
    :param user: A string which represents a slack user
    :param time_period: Only messages sent within the last "time_period" seconds will be deleted
    :return: A json object which represents the view of the "purge_confirmation" modal
    """

    # Retrieve modal and add number of messages
    modal = get_block_view("purge_confirmation.json").replace("%%NUMBER_OF_MESSAGES%%", str(number_of_messages))
    modal = json.loads(modal)

    # Specify content
    modal["blocks"][0]["text"]["text"] += f" which contains {text_snippet}" if text_snippet != "" else ""

    # Specify messages from which user
    modal["blocks"][0]["text"]["text"] += f" from user {user}" if user != "" else ""

    # Specify the time period
    modal["blocks"][0]["text"]["text"] += f" within the last {time_period} seconds" if time_period > 0 else ""

    # Save the details in the metadata
    modal["private_metadata"] = json.dumps({
        "number_of_messages": number_of_messages, 
        "user": user, 
        "time_period": time_period,
        "channel_id": channel_id,
        "text_snippet": text_snippet
    })

    return modal


def app_home(data):
    # Load view
    view = get_block_view("app_home.json")

    # Add essential information
    view = view.replace("%%USERNAME%%", data["username"])
    view = view.replace("%%FULL_NAME%%", data["full_name"])
    view = view.replace("%%ROLE%%", data["role"])
    view = view.replace("%%JOIN_DATE%%", data["join_date"])
    view = view.replace("https://picsum.photos/200/300", data["image_original"])

    # Add profile details
    values = data["values"]
    for key in ["favourite_course", "favourite_programming_language", "favourite_netflix_show", "favourite_food", \
        "overrated", "underrated", "biggest_flex", "enrolled_courses", "completed_courses", "general_interests"]:
        view = view.replace(f"%%{key.upper()}%%", values[key] if key in values.keys() else "-")

    return json.loads(view)

def event_styling(event):

    # truncate description
    if len(event["description"]) > 100:
        event["description"] = event["description"][:100] + "..."

    # Load event styling
    event_structure = get_block_view("event_styling.json")
    event_structure = json.loads(event_structure)
    event_structure[0]["text"]["text"] = event_structure[0]["text"]["text"].replace("%%TITLE%%", event["title"])
    event_structure[0]["text"]["text"] = event_structure[0]["text"]["text"].replace("%%DESCRIPTION%%", event["description"])
    event_structure[0]["accessory"]["image_url"] = event_structure[0]["accessory"]["image_url"].replace("%%IMAGE_URL%%", event["image_url"])
    event_structure[0]["text"]["text"] = event_structure[0]["text"]["text"].replace("%%URL%%", event["url"])

    return event_structure


def events_modal(events, keyword, page_number):
    # Load modal
    modal = get_block_view("events_modal.json")

    # Add keyword to header
    modal = modal.replace("%%KEYWORD%%", keyword)
    modal = json.loads(modal)

    for event in events:
        modal["blocks"] += event_styling(event)

    # Load page context
    page_context = get_block_view("event_page_context.json").replace("%%PAGE_NUMBER%%", str(page_number))
    page_context = json.loads(page_context)
    modal["blocks"].append(page_context)

    return modal

