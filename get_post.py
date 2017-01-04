import praw

def lambda_handler(event, context):
    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]

    if intent_name == "Get":
        return get_posts(intent)

def on_session_ended(session_ended_request, session):
    print "Ending session."

def handle_session_end_request():
    card_title = "Reddit Headlines"
    speech_output = "Thank you for using Reddit Headlines."
    should_end_session = True

    return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))

def get_welcome_response():
    session_attributes = {}
    card_title = "Reddit Headlines"
    speech_output = "Welcome to Reddit Headlines. " \
                    "Ask me for the top posts on reddit right now."
    reprompt_text = "Ask me for however many posts you want to hear."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_posts(intent):
    session_attributes = {}
    reddit = praw.Reddit(client_id='8MhFkN6PtwLipA',
                         client_secret='8SCcMwepKyRu_yEgwsZYSd8kSIs',
                         password=">.9Z6~_'eTqR7;%W",
                         user_agent='scrapes titles from top posts to /r/all',
                         username='reddit-scraper-45')
    card_title = "Reddit Headlines"
    reprompt_text = ""
    should_end_session = True
    if "Count" in intent["slots"]:
        limit = int(intent["slots"]["Count"]["value"])
        if limit > 30:
            limit = 30
    else:
        limit = 1
    output = ""
    count = 1
    for submission in reddit.subreddit('all').hot(limit=limit):
        output += str(count) + '. To ' + str(submission.subreddit) + ': ' + str(submission.title) + '. '
        count += 1
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }