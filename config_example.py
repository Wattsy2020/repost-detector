# reddit account settings
username = ''
password = ''
client_id = ''
client_secret = ''
user_agent = ''

subreddit = ''  # the subreddit the bot searches through
update_hour = 12  # the hour of the day when the bot will add new posts to it's archive (24hr time)
max_post_age = 3600  # the bot won't check new posts that are older than this (units are seconds)
min_similarity = .85  # minimum similarity for the bot to recognise an image as a repost. Recommend not changing
min_post_score = 500  # the bot won't record posts with less upvotes than this
colour_bins = [8, 12, 8]  # used to setup the image search engine. Don't change without reading the README

message = '''Accusation: General Reposti!

Observation: This post appears to be similar to [post_title](post_link)

Query: May I eliminate the meatbag master?



[Source code](https://github.com/Wattsy2020/repost-detector)'''
# please leave this ^ line in
