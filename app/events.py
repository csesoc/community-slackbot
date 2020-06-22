from app import slack_events_adapter, slack_token, client
from app.event_handlers.stylecheck import handle_style_check_request


@slack_events_adapter.on("message")
def reply(event_data):
    print(event_data)
    channel = event_data["event"]["channel"]
    if event_data['token'] != slack_token and 'text' in event_data['event']:
        if event_data['event']['text'].startswith("stylecheck"):
            handle_style_check_request(client, slack_token, event_data)
