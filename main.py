import os
import shutil
import time
import prawcore
from post_recorder import subreddit
from datetime import datetime

import post_recorder
from post_comparison import Post, NewPost, compare_keywords


def record_all_posts():
    start_month = int(datetime(2017, 1, 1).timestamp())
    end_month = int(datetime(2017, 2, 1).timestamp())

    while end_month < datetime.today().timestamp():
        post_recorder.record_old_posts(start_month, end_month, 1000)

        # this actually adds 30 days instead of 1 month but that doesn't matter much
        start_month = end_month
        end_month = end_month + 2592000

    # record the most recent posts using praw
    post_recorder.record_new_posts('month', 1000)


def load_all_posts():
    posts_folder = os.path.join(post_recorder.base_folder, 'top_posts')
    posts = []

    for folder in os.listdir(posts_folder):
        post_path = os.path.join(posts_folder, '{}\\data.txt'.format(folder.title()))

        if os.path.exists(post_path):  # if its a deleted post it will have a folder but no text file
            posts.append(Post(post_path))

    posts = sorted(posts, key=lambda item: -item.date)  # need negative sign to sort by most recent date

    return posts


def update_posts():
    post_recorder.record_new_posts('day', 35)

    # it may seem overkill to reload every single post but it doesn't take that long compared to check_if_repost
    return load_all_posts()


def reply(repost: NewPost, original):
    print('\n{} is a repost of {}'.format(repost.link, original.link))


def check_if_repost(new_post):
    # print('\nChecking: {}       Meme text: {}'.format(new_post.title, new_post.meme_words))
    title_similarity_limit = .7
    meme_text_similarity_limit = .7
    image_similarity_limit = .9

    # compare posts with the same title
    temp_folder = os.path.join(post_recorder.base_folder, 'temp')
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder, get_text=False)

        # handle gifs
        if new_post.image_path == '' or search_post.image_path == '':
            if new_post.image_path == search_post.image_path and new_post.title == search_post.title \
                    and len(new_post.title) > 20:
                reply(new_post, search_post)
                shutil.rmtree(temp_folder)
                return
            shutil.rmtree(temp_folder)
            continue

        similarity = new_post.compare_image(search_post)
        shutil.rmtree(temp_folder)

        if similarity >= image_similarity_limit:
            reply(new_post, search_post)
            return

    # search for posts with similar meme_words and use image comparison on the matches
    for post in posts:
        # ignore gifs
        if new_post.image_path == '' or post.image_path == '':
            continue

        # compare blank images
        elif not new_post.meme_words:
            if compare_keywords(new_post.title_keywords, post.title_keywords) >= title_similarity_limit:
                if new_post.compare_image(post) >= image_similarity_limit:
                    reply(new_post, post)
                    return

        # compare normal image post
        elif compare_keywords(new_post.meme_words, post.meme_words) >= meme_text_similarity_limit:
            if new_post.compare_image(post) >= image_similarity_limit:
                reply(new_post, post)
                return


def main():
    new_folder = os.path.join(post_recorder.base_folder, 'new')
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)

    while True:
        process_start_time = datetime.today()

        for i, submission in enumerate(subreddit.top('hour')):
            post_folder = os.path.join(new_folder, str(i))
            post = NewPost(submission, post_folder)

            # handle internet dropouts
            try:
                check_if_repost(post)
            except prawcore.exceptions.ServerError:
                time.sleep(180)

            if process_start_time.hour < datetime.today().hour:
                break

        print('Refreshing posts at {0:02d}'.format(datetime.today().hour)+':{0:02d}'.format(datetime.today().minute))

        # clear the new posts directory
        shutil.rmtree(new_folder)
        os.mkdir(new_folder)

        if process_start_time.day < datetime.today().day:
            posts = update_posts()


posts = load_all_posts()
if __name__ == '__main__':
    main()
