import os
import shutil
import time
import prawcore
from datetime import datetime

import post_recorder
import message
from post_recorder import subreddit
from post_comparison import Post, NewPost


def record_all_posts(posts_per_month):
    start_month = int(datetime(2017, 1, 1).timestamp())
    end_month = int(datetime(2017, 2, 1).timestamp())

    while end_month < datetime.today().timestamp():
        post_recorder.record_old_posts(start_month, end_month, posts_per_month)

        # this actually adds 30 days instead of 1 month but that doesn't matter much
        start_month = end_month
        end_month += 2592000

    # record the most recent posts using praw
    post_recorder.record_new_posts('month', posts_per_month)


def load_all_posts():
    posts_folder = os.path.join(post_recorder.base_folder, 'top_posts')

    posts = [Post(os.path.join(posts_folder, i.title()+'\\data.txt')) for i in os.listdir(posts_folder)]
    return sorted(posts, key=lambda item: -item.date)  # need negative sign to sort by most recent date


def update_posts():
    post_recorder.record_new_posts('day', 35)

    # this is performed during a low traffic time so performance is not an issue, can reuse load_all_posts
    return load_all_posts()


def reply(repost: NewPost, original):
    '''
    reply_message = message.get_message(original.title, original.link)

    # handle deleted posts
    try:
        repost.submission.reply(reply_message)
    except praw.exceptions.APIException:
        return
    '''
    pass


def check_if_repost(new_post):
    # print('\nChecking: {}       Meme text: {}'.format(new_post.title, new_post.meme_words)
    image_similarity_limit = .85

    # compare posts with the same title
    temp_folder = os.path.join(post_recorder.base_folder, 'temp')
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder)

        # ignore gifs
        if new_post.image_path == '' or search_post.image_path == '':
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

        # to do: write reverse image search to find possible reposts and use compare_image to confirm


def main():
    process_start_time = datetime.today()

    for submission in subreddit.stream.submissions():
        post_age = datetime.today().timestamp() - submission.created_utc
        if post_age > 3600: continue  # so the bot can be restarted without analysing a backlog of posts
        print(post_age)

        post = NewPost(submission, new_folder)

        # handle internet dropouts
        try:
            check_if_repost(post)
        except prawcore.exceptions.ServerError:
            time.sleep(180)

        shutil.rmtree(new_folder)

        # update posts when there is low traffic (adjust hour depending on your timezone)
        if process_start_time.day < datetime.today().day and datetime.today().hour == 12:
            print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                  + ':{0:02d}'.format(datetime.today().minute))

            global posts
            posts = update_posts()
            process_start_time = datetime.today()


new_folder = os.path.join(post_recorder.base_folder, 'new')
posts = load_all_posts()

if __name__ == '__main__':
    main()
