import hashlib
import hmac
import os

from app import db
from app.models import AnonMsgs, Report, User, Roles, UserRole


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
    slack_signing_secret = os.environ['SLACK_SIGNING_SECRET']
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
    anon = AnonMsgs(user_id=sender_id, target_id=msg.target_id, msg=reply_msg)
    db.session.add(anon)
    db.session.commit()
    return anon


def report_message(msg_id, report):
    report = Report(msg_id=msg_id, report=report)
    db.session.add(report)
    db.session.commit()
    return report.id


def get_role_title(role_id):
    role = Roles.query.filter_by(id=role_id).first()
    return role.title


def get_role_id_by_perm_level(perm_level):
    role = Roles.query.filter_by(perm_level=perm_level).first()
    return role.id


def retrieve_highest_permission_level(user_id):
    """
    Retrieve highest permission level of a given user_id
    :param user_id: A string of 11 characters representing a slack user id
    :return: An integer that represents the highest permission level for the given user
    """

    # Retrieve all roles of given user
    role_ids = [user_role.role_id for user_role in UserRole.query.filter_by(user_id=user_id).all()]

    max_role = Roles.query.filter(Roles.id.in_(role_ids))\
        .order_by(Roles.perm_level.desc())\
        .first()
    if max_role is None:
        return 0
    return max_role.id
