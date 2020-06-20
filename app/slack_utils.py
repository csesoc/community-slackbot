import hashlib
import hmac
import os

# Set up db
# TODO: Replace below with:
# from . import db
# and add database functionality to the user functions
users = []
user_profile_details = []


def verify_request(request):
    """
    Verifies slack request
    :param request
    :param secret
    :return: Is request verified
    """
    timestamp = request.headers['X-Slack-Request-Timestamp']
    data = request.get_data()
    slack_signature = request.headers['X-Slack-Signature']
    sig_basestring = str.encode('v0:' + timestamp + ':') + data
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
    secret = str.encode(slack_signing_secret)
    my_signature = 'v0=' + hmac.new(key=secret, msg=sig_basestring, digestmod=hashlib.sha256).hexdigest()
    if hmac.compare_digest(my_signature, slack_signature):
        return True
    return False


def add_new_user(user):
    """
    Add a user to the database
    :param user: A string of 9 characters representing a slack user id
    """
    users.append(user)


def query_user_exists(user):
    """
    Checks if a user is in the database
    :param user: A string of 9 characters representing a slack user id
    :return: Bool 
    """
    return True if user in users else False


def add_profile_details(user, key, value):
    """
    Add details of a user to the database.
    :param user: A string of 9 characters representing a slack user id
    :param key: The key used for storing and accessing the value
    :param value: The value to be stored and accessed.
    """

    # Remove exisiting details for the particular user and key in the database 
    try:
        user_profile_details.remove(
            [i for i in user_profile_details if i["user"] == user and i["key"] == key][0]
        )
    except:
        pass

    # If the value is None then skip instead of adding to the database 
    if value == "":
        return

    # Add the new key value pair to the database
    user_profile_details.append({
        "user": user,
        "key": key,
        "value": value
    })

    # Debug. TODO: Remove
    print(f'{user}:{key}="{value}"')

def retrieve_profile_details(user):
    """
    Retrieve profile details from given user
    :param user: A string of 9 characters representing a slack user id
    :return: A dictionary of key values pairs representing the details for the given user
    """

    # Intialise a dictionary to store the details
    details = {}

    # Retrieve the raw details from the database
    raw_details = [detail for detail in user_profile_details if detail["user"] == user]

    # Convert the raw details into a usable dict format
    for item in raw_details:
        details[item["key"]] = item["value"]

    # Return the key value pairs
    return details


def extract_value(values, block_id, action_id):
    """
    Extract values from "view_submission" payloads, by accessing the nested values within the state values.
    :param values: The "values" object in the "state" section of a slack "view_submissions" payload.
    :param block_id: The block_id to use to extract the value
    :param action_id: The action_id to use to extract the value
    :return: The extracted value as a string. Can be an empty string if value does not exist.
    """
    return values[block_id][action_id]["value"] if "value" in values[block_id][action_id].keys() else ""
