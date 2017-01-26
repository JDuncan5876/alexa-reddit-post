import praw
import re

reddit = praw.Reddit(client_id="8MhFkN6PtwLipA",
                     client_secret="8SCcMwepKyRu_yEgwsZYSd8kSIs",
                     password=">.9Z6~_'eTqR7;%W",
                     user_agent="scrapes titles from top posts to reddit",
                     username="reddit-scraper-45")

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
        return handle_continue_request(session)
    elif intent_name == "GetContent":
        return handle_get_content_request(intent, session)
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
    session_attributes = {"LastState": "Launch"}
    card_title = "Reddit Headlines"
    speech_output = "Welcome to Reddit Headlines. " \
                    "Ask me for the top posts on reddit right now."
    reprompt_text = "Ask me for however many posts you want to hear."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_posts(intent):
    session_attributes = {"LastState": "Get"}
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
    card_output = output
    count = 1
    for submission in reddit.subreddit(sub).hot(limit=limit):
        output += str(count) + '. '
        if sub == "all":
            output += "To " + str(submission.subreddit) + ": "
        output += submission.title.encode("ascii", "ignore") + ". "
        count += 1
    output += " Would you like to hear the content of any of these posts?"
    output = re.sub(r'\(?http[^ \n)]*\)?', '', output)
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session, card_output))

def handle_continue_request(session):
    if session["attributes"]["LastState"] == "GetContent":
        content_status = int(session["attributes"]["get_content_status"])
        post_id = str(session["attributes"]["post_id"])
        submission = reddit.submission(post_id)
        return get_content(submission, content_status)
    else:
        return continue_prompt()

def continue_prompt():
    session_attributes = {"LastState": "Continue"}
    card_title = "Reddit Headlines"
    output = ""
    reprompt_text = "Which post would you like to hear?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session))

def handle_get_content_request(intent, session):
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
    return get_content(final_submission, 0, post_num)


def get_content(submission, content_status, post_num=None):
    card_title = "Reddit Headlines"
    reprompt_text = ""
    should_end_session = False
    if submission.selftext == "":
        output = "This post is not a self post. I can only read self posts."
    else:
        output = submission.selftext.encode('ascii', 'ignore')
    output += " Would you like to hear the output of any other posts?" #TODO: fix bug where this and continue prompt appears
    output = re.sub(r'\(?http[^ \n)]*\)?', '', output)
    output = output[content_status * 5000:]
    if len(output) > 6000:
        output = output[:5000 + content_status * 5000] + ". I'm sorry, I can't read any more. Would you like to hear more?"
        session_attributes = {"get_content_status": content_status + 1,
            "post_id": submission.id,
            "LastState": "GetContent"}
    else:
        session_attributes = {"LastState": "Continue"}
    if content_status == 0:
        intro = "Getting post " + str(post_num) + " from " + str(submission.subreddit) + ", "
        intro += "titled " + submission.title.encode('ascii', 'ignore') + '. '
        output = intro + output
        card_output = intro
    else:
        card_output = ""
    return build_response(session_attributes, build_speechlet_response(
        card_title, output, reprompt_text, should_end_session, card_output))


def build_speechlet_response(title, output, reprompt_text, should_end_session, card_output=None):
    if card_output == None:
        card_output = output
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": card_output
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