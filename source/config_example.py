# reddit account settings
username = ''
password = ''
client_id = ''
client_secret = ''
user_agent = 'repost_detectorv1.0default_name'

subreddit = ''  # the subreddit the bot searches through
subreddit_creation_month = 1
subreddit_creation_year = 2017
update_hour = 12  # the hour of the day when the bot will add the top posts of the day to it's archive (24hr time)
min_similarity = .85  # minimum similarity for the bot to recognise an image as a repost. Recommend not changing
min_post_score = 500  # the bot won't record posts with less upvotes than this
colour_bins = [8, 12, 8]  # used to setup the image search engine. Don't change without reading the README
max_image_size = [900, 900]  # resizes images with dimensions larger than this

message = '''Accusation: General Reposti!

Observation: This post's image is {}% similar to [{}](http://{})

&nbsp;

I'm a bot [Source code](https://github.com/Wattsy2020/repost-detector)
My post has a different title, why does it think it's a repost? Most reposts have irrelevant titles so I ignore titles'''
# please leave this ^ line in
