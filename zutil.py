import settings
import hashlib
import hmac
import os

# Set up db
users = []

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
    Add user to the database
    """
    users.append(user)

def query_user_exists(user):
    """
    Checks if a user is in the database
    """
    return True if user in users else False

def add_profile_attributes(user, key, value):
    """
    Add attributes of a user to the database
    """
    if value is None:
        return

    print(f'{user}:{key}="{value}"')

def extract_value(values, block_id, action_id):
    """
    Extract values from "view_submission" payloads, by accessing the nested values within the state values.
    """
    return values[block_id][action_id]["value"] if "value" in values[block_id][action_id].keys() else None

