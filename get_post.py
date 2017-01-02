import praw

user = raw_input('username: ')
password = raw_input('password: ')
reddit = praw.Reddit(client_id='UdaaUL5eYb7V_A',
                     client_secret='Cn_dAQQ7rR7P-ucHaluTdtwda28',
                     password=password,
                     user_agent='testscript by /u/DerivedIntegral115',
                     username=user)
for submission in reddit.front.hot(limit=1):
    print 'The current top post on reddit is to /r/' + str(submission.subreddit) + ': ' + str(submission.title)