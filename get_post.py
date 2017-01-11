import praw
import re

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
    elif intent_name == "Continue":
        return continue_prompt()
    elif intent_name == "GetContent":
        return get_content(intent)
    else:
        return handle_session_end_request()

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
                         user_agent='scrapes titles from top posts to reddit',
                         username='reddit-scraper-45')
    card_title = "Reddit Headlines"
    reprompt_text = "Would you like to hear the content of any of these posts?"
    should_end_session = False
    try:
        limit = int(intent["slots"]["Count"]["value"])
    except:
        limit = 1
    try:
        sub = str(intent["slots"]["Subreddit"]["value"]).replace(" ", "")
    except:
        sub = "all"
    if limit > 30:
        limit = 30
    output = "Getting top " + str(limit) + " posts from " + sub + ". "
    count = 1
    for submission in reddit.subreddit(sub).hot(limit=limit):
        output += str(count) + '. '
        if sub == 'all':
            output += 'To ' + str(submission.subreddit) + ': '
        output += submission.title.encode('ascii', 'ignore') + '. '
        count += 1
    output += " Would you like to hear the content of any of these posts?"
    output = re.sub(r'\(?http[^ \n)]*\)?', '', output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session))

def continue_prompt():
    session_attributes = {}
    card_title = "Reddit Headlines"
    output = ""
    reprompt_text = "Which post would you like to hear?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session))

def get_content(intent):
    session_attributes = {}
    reddit = praw.Reddit(client_id='8MhFkN6PtwLipA',
                         client_secret='8SCcMwepKyRu_yEgwsZYSd8kSIs',
                         password=">.9Z6~_'eTqR7;%W",
                         user_agent='scrapes titles from top posts to reddit',
                         username='reddit-scraper-45')
    card_title = "Reddit Headlines"
    reprompt_text = "Would you like to hear the content of another post?"
    should_end_session = False
    try:
        post_num = int(intent["slots"]["PostNumber"]["value"])
    except:
        post_num = 1
    if post_num < 1 or post_num > 30:
        post_num = 1
    try:
        sub = str(intent["slots"]["Subreddit"]["value"]).replace(" ", "")
    except:
        sub = "all"
    for submission in reddit.subreddit(sub).hot(limit=post_num):
        final_submission = submission

    output = "Getting post " + str(post_num) + " from " + sub + ", "
    output += "titled " + final_submission.title.encode('ascii', 'ignore') + '. '
    if final_submission.selftext == "":
        output += "This post is not a self post. I can only read self posts."
    else:
        output += final_submission.selftext.encode('ascii', 'ignore')
    output += " Would you like to hear the output of any other posts?"
    output = re.sub(r'\(?http[^ \n)]*\)?', '', output)
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