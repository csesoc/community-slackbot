#helper functions for handler 

import hashlib
import hmac
import os
import re
import requests
import datetime
import time
import json
from bs4 import BeautifulSoup
from urllib.parse import quote

from app import db
from app.block_views import get_block_view
from app.models import User, UserProfileDetail, Roles, AnonMsgs, Report, UserRole, Review, Courses
from config import Config


def verify_request(request):
    """
    Verifies slack request
    :param request
    :return: Is request verified
    """
    timestamp = request.headers['X-Slack-Request-Timestamp']
    data = request.get_data()
    slack_signature = request.headers['X-Slack-Signature']
    sig_basestring = str.encode('v0:' + timestamp + ':') + data
    slack_signing_secret = Config.SLACK_SIGNING_SECRET
    secret = str.encode(slack_signing_secret)
    my_signature = 'v0=' + hmac.new(key=secret, msg=sig_basestring, digestmod=hashlib.sha256).hexdigest()
    if hmac.compare_digest(my_signature, slack_signature):
        return True
    return False


def create_anon_message(sender_id, target_ids, msg):
    msg_ids = []
    for target_id in target_ids:
        anon = AnonMsgs(user_id=sender_id, target_id=target_id, msg=msg)
        db.session.add(anon)
        db.session.commit()
        msg_ids.append(anon.id)
    return msg_ids


def reply_anon_message(sender_id, msg_id, reply_msg):
    # Should we flag as reply
    msg = AnonMsgs.query.filter_by(id=msg_id).first()
    anon = AnonMsgs(user_id=sender_id, target_id=msg.user_id, msg=reply_msg)
    db.session.add(anon)
    db.session.commit()
    return anon


def report_message(msg_id, report):
    report = Report(msg_id=msg_id, report=report)
    db.session.add(report)
    db.session.commit()
    return report.id


def close_report(report_id):
    Report.query.filter_by(id=report_id).delete()
    db.session.commit()


def get_role_title(perm_level):
    role = Roles.query.filter_by(perm_level=perm_level).first()
    return role.title


def get_role_id_by_perm_level(perm_level):
    role = Roles.query.filter_by(perm_level=perm_level).first()
    return role.id


def get_anon_message_from_id(msg_id):
    return AnonMsgs.query.filter_by(id=msg_id).first()


def retrieve_highest_permission_level(user_id):
    """
    Retrieve highest permission level of a given user_id
    :param user_id: A string of 11 characters representing a slack user id
    :return: An integer that represents the highest permission level for the given user,
             and the corresponding role title
    """

    # Retrieve all roles of given user
    query = Roles.query.filter_by(user_id=user_id).all()

    # Set permission level to the highest of the roles or 0 if user does not have any roles
    perm_level = max(role.perm_level for role in query) if query != [] else 0
    role = Roles.query.filter_by(user_id=user_id, perm_level=perm_level).first()
    title = role.title if role is not None else "Member"

    return perm_level, title


def extract_value(values, block_id, action_id):
    """
    Extract values from "view_submission" payloads, by accessing the nested values within the state values.
    :param values: The "values" object in the "state" section of a slack "view_submissions" payload.
    :param block_id: The block_id to use to extract the value
    :param action_id: The action_id to use to extract the value
    :return: The extracted value as a string. Can be an empty string if value does not exist.
    """
    return values[block_id][action_id]["value"] if "value" in values[block_id][action_id].keys() else ""


def jobs_from_indeed(page_number, query, options):
    """
    Retrieve a set of jobs from the indeed website, given the query string and page number.
    :param query: Query string which contains the job title, keywords, or company. Defaults
                  to "software internship"
    :param page_number: The page number of the results that you want to obtain. Defaults to 1.
    :return: Text that specifies the current set of jobs being shown, and an array of jobs.
    """

    # Make a request to the indeed website
    r = requests.get(f'https://au.indeed.com/jobs?q={quote(query)}&start={(page_number-1)*5}&limit=5{options}')

    # Extract the jobs from the html
    raw_jobs = re.findall('jobmap\[.*};', r.text)

    # Extract the text that specifies the number of jobs available
    try:
        message = BeautifulSoup(r.content, "html.parser").find(id="searchCountPages").get_text().strip()
        message += " | Indeed job search"

    # Return error message if no jobs found
    except:
        return f"The search {query} jobs did not match any jobs | Indeed job search", []

    # Array to store jobs
    jobs = []

    # Extract data from each job
    for job in raw_jobs:
        job = job[11:-1].strip()

        jobs.append({
            "link": "https://au.indeed.com/viewjob?jk=" + re.search("jk:'.*',efccid", job).group(0)[4:-8],
            "title": re.search("title:'.*',locid:", job).group(0)[7:-8].replace("\\", ""),
            "company": re.search("cmp:'.*',cmpesc:", job).group(0)[5:-9],
            "location": re.search("loc:'.*',country:", job).group(0)[5:-10]
        })

    return message, jobs


def retrieve_created_at(user):
    datetime_obj = User.query.filter_by(id=user).first()
    datetime_str = datetime_obj.created_at.strftime("%d/%m/%y") if datetime_obj is not None else "00/00/00"
    return datetime_str

def add_new_user(user, is_admin=False, is_owner=False):
    """
    Add a user to the database
    :param user: A string of 9 characters representing a slack user id
    """
    db.session.add(User(id=user))
    db.session.commit()

    if is_owner:
        db.session.add(Roles(user_id=user, title="owner", perm_level=2))
        db.session.commit()
    elif is_admin:
        db.session.add(Roles(user_id=user, title="admin", perm_level=1))
        db.session.commit()


def query_user_exists(user):
    """
    Checks if a user is in the database
    :param user: A string of 9 characters representing a slack user id
    :return: Bool 
    """
    return True if User.query.filter_by(id=user).first() is not None else False


def add_profile_details(user, key, value):
    """
    Add details of a user to the database.
    :param user: A string of 9 characters representing a slack user id
    :param key: The key used for storing and accessing the value
    :param value: The value to be stored and accessed.
    """

    # Retrieve details for given user and key 
    details = UserProfileDetail.query.filter_by(user_id=user, detail_key=key)

    for detail in details:
        # Return if value is already set
        if detail.value == value:
            return

        # Delete detail
        db.session.delete(detail)
        db.session.commit()

    # Adds the detail to the database if the value is not an empty string 
    if value != "":
        db.session.add(UserProfileDetail(user_id=user, detail_key=key, value=value))
        db.session.commit()   


def retrieve_profile_details(user):
    """
    Retrieve profile details from given user
    :param user: A string of 9 characters representing a slack user id
    :return: A dictionary of key values pairs representing the details for the given user
    """

    # Intialise a dictionary to store the details
    details = {}

    # Retrieve the raw details from the database
    raw_details = UserProfileDetail.query.filter_by(user_id=user)

    # Convert the raw details into a usable dict format
    for item in raw_details:
        details[item.detail_key] = item.value

    # Return the key value pairs
    return details

def retrieve_event_details(keyword, page):

    if keyword == "" or keyword == "unsw":
        r = requests.get(f'https://dev-api.linkupevents.com.au/events?uni=unsw&limit=5&offset={page * 5}')
    elif keyword == "cse":
        r = requests.get(f'https://dev-api.linkupevents.com.au/events?uni=unsw&society_id=csesoc')

    events = json.loads(r.text)

    # Filter events for necessary info
    rtn = []
    for event in events:
        rtn.append({
            "url": event["url"],
            "title": event["title"],
            "description": event["description"],
            "image_url": event["image_url"]
        })

    return rtn

def get_top_karma():
    return User.query.order_by(User.karma.desc()).limit(5).all()

def add_karma(u_id):
    user = User.query.filter_by(id=u_id).first()
    user.karma = user.karma + 1
    db.session.commit()

def remove_karma(u_id):
    user = User.query.filter_by(id=u_id).first()
    user.karma = user.karma - 1
    db.session.commit()

def get_starting_date():
    """
    Returns the date of the first day of the starting week which starts on a monday
    """
    date = datetime.date.today()
    while (date.weekday() != 0):
        date = date - datetime.timedelta(1)
    return date

def get_previous_date(date):
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    return date.date() - datetime.timedelta(7)

def get_next_date(date):
    date = datetime.datetime.strptime(str(date), "%Y-%m-%d")
    return date.date() + datetime.timedelta(7)

def get_timetable_data(date):
    # Dummy data as we cannot yet experiment with the timetable in the database.
    # TODO: Connect to database
    if str(date) == '2020-12-14':
        return {
            "monday": [
                {
                    "title": "COMP2511 O-O Design & Programming Tut-Lab H09A",
                    "time": "9:00am - 12:00pm"
                },
                {
                    "title": "COMP3121 Algorithms and Programming Techniques Lecture LEC1",
                    "time": "1:00pm - 3:00pm"
                }
            ],
            "tuesday": [
                {
                    "title": "MATH2701 Algebra and Analysis Lecture A",
                    "time": "11:00am - 2:00pm"
                }
            ],
            "wednesday": [],
            "thursday": [],
            "friday": [
                {
                    "title": "MATH2701 Algebra and Analysis Lecture B",
                    "time": " 6:00pm - 9:00pm"
                }
            ],
            "saturday": [],
            "sunday": []
        }
    elif str(date) == '2020-12-21':
        return {
            "monday": [
                {
                    "title": "COMP2511 O-O Design & Programming Tut-Lab H09A",
                    "time": "9:00am - 12:00pm"
                }
            ],
            "tuesday": [],
            "wednesday": [],
            "thursday": [
                {
                    "title": "COMP3121 Algorithms and Programming Techniques Lecture LEC1",
                    "time": "1:00pm - 3:00pm"
                }
            ],
            "friday": [
                {
                    "title": "MATH2701 Algebra and Analysis Lecture B",
                    "time": " 6:00pm - 9:00pm"
                }
            ],
            "saturday": [],
            "sunday": []
        }
    else:
        return {
            "monday": [],
            "tuesday": [],
            "wednesday": [],
            "thursday": [],
            "friday": [],
            "saturday": [],
            "sunday": []
        }   

def get_user_review_block(review) -> str:
    item = get_block_view("views/courses/user_review.json")
    item = item.replace("{LECTURER}", review.lecturer)
    item = item.replace("{TERM}", review.term)
    item = item.replace("{THOUGHTS}", review.review)

    item = item.replace("{OVERALL}", "{} ({:.1f}/5)".format(review.overall * ":star:", review.overall))
    item = item.replace("{DIFFICULTY}", "{} ({:.1f}/5)".format(review.difficulty * ":star:", review.difficulty))
    item = item.replace("{TIME}", "{} ({:.1f}/5)".format(review.time * ":star:", review.time))

    return item


def get_course_summary_block(course) -> str:
    item = get_block_view("views/courses/course_summary.json")
    item = item.replace("{COURSE NAME}", course.course)
    item = item.replace("{COURSE_SHORT_SUMMARY}", course.msg)

    reviews = Review.query.filter_by(course=course.course).all()
    num_reviews = len(reviews)
    item = item.replace("{NUM_REVIEWS}", str(num_reviews))
    reviews_str = ""

    overall_rating = 0.0
    overall_difficulty = 0.0
    overall_time = 0.0
    for review in reviews:
        overall_rating += review.overall
        overall_time += review.time
        overall_difficulty += review.difficulty

    if num_reviews > 0:
        overall_time /= num_reviews
        overall_rating /= num_reviews
        overall_difficulty /= num_reviews
        reviews_str = "," + ",".join([get_user_review_block(review) for review in reviews])
        item = item.replace("{OVERALL}", "{} ({:.1f}/5)".format(int(overall_rating) * ":star:", overall_rating))
        item = item.replace("{DIFFICULTY}", "{} ({:.1f}/5)".format(int(overall_difficulty) * ":star:", overall_difficulty))
        item = item.replace("{TIME}", "{} ({:.1f}/5)".format(int(overall_time) * ":star:", overall_time))
        item = item.replace("{USER_REVIEWS}", reviews_str)
    
    else:
        item = get_block_view("views/courses/course_summary_reviewless.json")
        item = item.replace("{COURSE NAME}", course.course)
        item = item.replace("{COURSE_SHORT_SUMMARY}", course.msg)

    return item


def get_full_name_from_uid(user_id: str) -> str:
    info_endpoint = f"https://slack.com/api/users.info?token={Config.SLACK_BOT_TOKEN}&user={user_id}"
    user_info = requests.get(info_endpoint).json()
    return user_info["user"]["real_name"]
def get_courses():
    return Courses.query.all()
