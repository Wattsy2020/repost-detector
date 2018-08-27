import os
import shutil
import time
import prawcore
from threading import Thread
from datetime import datetime

import post_recorder
import image_search
import config
from post_recorder import subreddit, reddit
from post_comparison import Post, NewPost


def load_all_posts():
    posts_folder = post_recorder.base_post_folder
    posts = [Post(os.path.join(posts_folder, i.title()+'\\data.txt')) for i in os.listdir(posts_folder)]

    # sort by id so that posts[post id] gives you the post with that id
    return sorted(posts, key=lambda post: post.id)


def update_posts():
    # add all posts that are older than a day and have enough upvotes to the archive
    for _ in range(len(new_submissions)):
        if new_submissions[0].score > config.min_post_score:
            post_recorder.record_submission(new_submissions[0])
        if (datetime.today().timestamp() - new_submissions[0].created_utc) > 86400:
            new_submissions.pop(0)

    # refresh image_searcher to load in the updated index.csv file
    global image_searcher
    image_searcher = image_search.ImageSearcher(post_recorder.index_file)

    # this is performed during a low traffic time so performance is not an issue, can reuse load_all_posts
    return load_all_posts()


def clear_folders():
    if os.path.exists(new_folder): shutil.rmtree(new_folder)
    if os.path.exists(temp_folder): shutil.rmtree(temp_folder)


def reply(repost: NewPost, original, similarity):
    message = config.message.format(similarity*100, original.title, original.link)
    repost.submission.reply(message)


def check_if_repost(new_post):
    # compare posts with the same title
    for submission in subreddit.search("title:{}".format(new_post.title), sort='top'):
        # ignore the exact same post
        if new_post.link == ('reddit.com'+submission.permalink): continue
        if submission.score <= 25: break

        search_post = NewPost(submission, temp_folder)
        if not search_post.image_path:
            shutil.rmtree(temp_folder)
            continue

        similarity = new_post.compare_image(search_post)
        shutil.rmtree(temp_folder)

        if similarity >= config.min_similarity:
            reply(new_post, search_post, similarity)
            return

    # search through stored posts with similar colour histograms and reply to the ones that are structurally similar
    results = [posts[result[0]] for result in image_searcher.search(new_post.features)]
    for similar_post in results:
        similarity = new_post.compare_image(similar_post)
        if similarity >= config.min_similarity:
            reply(new_post, similar_post, similarity)
            return


def main():
    process_start_time = datetime.today()
    last_post_timestamp = 0  # track when the last post analysed was created

    # this is wrapped in a try except to prevent internet dropouts crashing the bot
    while True:
        try:
            for submission in subreddit.stream.submissions():
                # so the bot won't analyse old posts if an exception occurs and the stream restarts
                if submission.created_utc < last_post_timestamp: continue
                if datetime.today().timestamp() - submission.created_utc > 1800: continue

                post = NewPost(submission, new_folder)
                if post.image_path:
                    print("Checking: {}".format(post.link))
                    check_if_repost(post)
                    new_submissions.append(submission)

                shutil.rmtree(new_folder)
                last_post_timestamp = submission.created_utc

                # update posts when there is low traffic
                if process_start_time.day < datetime.today().day and datetime.today().hour == config.update_hour:
                    print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                          + ':{0:02d}'.format(datetime.today().minute))

                    global posts
                    posts = update_posts()
                    process_start_time = datetime.today()

        except prawcore.exceptions.ServerError:
            print("Error occured while connecting to reddit, restarting stream")
        except Exception as e:
            print("\n\n\nError occured: {}".format(e))
            print("If this isn't an internet connection error please report it "
                  "at https://github.com/Wattsy2020/repost-detector/issues\n\n\n")
        time.sleep(300)
        clear_folders()


def remove_false_positives():
    """Delete downvoted comments as they are false positives"""

    bot_account = reddit.redditor(config.username)
    while True:
        try:
            for comment in bot_account.comments.new(limit=20):
                if comment.ups < -1: comment.delete()
            time.sleep(900)
        except prawcore.exceptions.ServerError:
            time.sleep(300)


new_folder = os.path.join(post_recorder.base_folder, 'new')
temp_folder = os.path.join(post_recorder.base_folder, 'temp')
clear_folders()

# used to store new posts so that they can be added to top_posts later
new_submissions = [post for post in subreddit.top('day', limit=1000)]

posts = load_all_posts()
image_searcher = image_search.ImageSearcher(post_recorder.index_file)
# I ran into a bug with this so am just leaving this here in case
assert len(image_searcher.index) == len(posts), "Index size not equal to number of posts"

if __name__ == '__main__':
    Thread(name="Remove False Positives", target=remove_false_positives).start()
    Thread(name="Main", target=main).start()
