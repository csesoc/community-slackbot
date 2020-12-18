import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests

from config import Config

EMAIL_FROM_ADDR = 'noreply.csesoc.slack@gmail.com'
PASSWORD_EMAIL_SUBJECT = 'CSESOC Slack Channel Notification'


def send_important_email_notification(channel_name: str, channel_id: str, sending_user: str = None):
    """
    Format and send important slash command email notifications (Note you need the users:read.email scope to get emails)

    :param channel_name: Name of channel notifying of
    :param channel_id: Channel id of channel notifying of
    :param sending_user: User id of user who made request
    :return: None
    """

    members_endpoint = 'https://slack.com/api/conversations.members?token=%s&channel=%s' % (
        Config.SLACK_BOT_TOKEN, channel_id)
    response_payload = requests.get(members_endpoint).json()
    members = response_payload.get("members", None)
    if members is None:
        return
    print(members)
    users_list = []
    for user_id in members:
        if user_id != sending_user:
            info_endpoint = f"https://slack.com/api/users.info?token={Config.SLACK_BOT_TOKEN}&user={user_id}"
            user_info = requests.get(info_endpoint).json()
            users_list.append(user_info["user"])
    users_to_send_email_to = []
    for user in users_list:
        if "email" in user['profile']:
            users_to_send_email_to.append([user['profile']['email'], user["profile"]["real_name"]])

    # Check if email configured
    if not Config.SMTP_HOST:
        return

    for recipient in users_to_send_email_to:
        recipient_email, name = recipient
        message = f"Hello {name}, there is a notification for channel: {channel_name} on the CSESOC Slack. " \
                  f"See it at https://app.slack.com/client/T017ANU0DL7/{channel_id}"
        print(f"Sending email: {message}")
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM_ADDR
        msg['To'] = recipient_email
        msg['Subject'] = PASSWORD_EMAIL_SUBJECT
        msg.attach(MIMEText(message))
        if Config.SMTP_SEND_MAIL:
            smtp = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
            smtp.ehlo()
            if Config.SMTP_USE_TLS:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(Config.EMAIL_LOGIN, Config.EMAIL_PASSWORD)
            smtp.sendmail(EMAIL_FROM_ADDR, recipient_email, msg.as_string())
            smtp.quit()
