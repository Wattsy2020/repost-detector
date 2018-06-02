import re

import praw
import config
import os
import urllib
import text_recognition


def get_subreddit():
    reddit = praw.Reddit(username=config.username,
                         password=config.password,
                         client_id=config.client_id,
                         client_secret=config.client_secret,
                         user_agent='prequelmemes-repost-bot-v0.1')

    subreddit = reddit.subreddit('prequelmemes')
    return subreddit


def store_post(data, folder):
    file_path = os.path.join(folder, "data.txt")

    with open(file_path, 'w', encoding="utf-8") as file:
        for field in data:
            file.write(str(field)+'\n')


def download_image(url, folder):
    # handle different image urls and ignore gifs
    if '.gif' in url:
        return ''
    if 'imgur' in url:
        url = url + '.jpg'
    elif 'i.redd' not in url:
        return ''

    file_name = os.path.join(folder, 'image.jpg')
    try:
        urllib.request.urlretrieve(url, file_name)
    except urllib.error.HTTPError:  # handle deleted images
        return ''
    except Exception as error:
        print('\n Error occurred while downloading image: {}'.format(error))
        return ''

    return file_name


def get_post_data(post, folder, get_text=True):
    title = post.title
    title = re.sub('[^a-zA-Z0-9\s]+', '', title)  # subreddit.search(title) throws errors with weird characters

    score = post.score
    date = int(post.created_utc)
    link = "reddit.com{}".format(post.permalink)
    image_path = download_image(post.url, folder)

    title_words = text_recognition.get_words(title)
    title_keywords = text_recognition.remove_common_words(title_words)

    if get_text:
        meme_text = text_recognition.get_image_text(image_path)
        meme_words = text_recognition.get_words(meme_text)
        meme_keywords = text_recognition.parse_ocr_text(meme_words)
    else:
        meme_keywords = ['']

    return title, title_keywords, link, score, date, image_path, meme_keywords


def record_top_posts(time_filter, amount):
    base_post_folder = os.path.join(base_folder, time_filter)

    if os.path.exists(base_post_folder):
        num_existing_posts = len(os.listdir(base_post_folder))
    else:
        os.mkdir(base_post_folder)
        num_existing_posts = 0

    for i, post in enumerate(subreddit.top(time_filter, limit=amount)):
        if i < num_existing_posts: continue  # don't recreate existing posts

        post_folder = os.path.join(base_post_folder, str(i))
        os.mkdir(post_folder)

        data = get_post_data(post, post_folder)
        store_post(data, post_folder)

        print("{}% complete".format(int((i+1)/amount*100)))


subreddit = get_subreddit()
base_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)))
