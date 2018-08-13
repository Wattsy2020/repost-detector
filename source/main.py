import os
import shutil
import time
import prawcore
from datetime import datetime

import post_recorder
import image_search
import config
from post_recorder import subreddit
from post_comparison import Post, NewPost


def load_all_posts():
    posts_folder = post_recorder.base_post_folder
    posts = [Post(os.path.join(posts_folder, i.title()+'\\data.txt')) for i in os.listdir(posts_folder)]

    # sort by id so that posts[post id] gives you the post with that id
    return sorted(posts, key=lambda post: post.id)


def update_posts():
    for post in new_posts:
        if (datetime.today().timestamp() - post.date) > 86400:  # if post is older than a day
            if post.submission.score > config.min_post_score:
                # store data using post_recorder.store_post in post.folder
                # copy post.folder into top_posts
                pass
            # remove post from new_posts array and storage folder
        else: break

    for i in range(len(new_posts)):
        # rename folder of post and post.folder to i
        pass

    # refresh image_searcher to load in the updated index.csv file
    global image_searcher
    image_searcher = image_search.ImageSearcher(post_recorder.index_file)

    # this is performed during a low traffic time so performance is not an issue, can reuse load_all_posts
    return load_all_posts()


def clear_folders():
    if os.path.exists(new_folder): shutil.rmtree(new_folder)
    if os.path.exists(temp_folder): shutil.rmtree(temp_folder)


def reply(repost: NewPost, original):
    message = config.message.format(original.title, original.link)
    # repost.submission.reply(message)


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
            reply(new_post, search_post)
            return

    # search through stored posts with similar colour histograms and confirm they are structurally similar
    results = [posts[result[0]] for result in image_searcher.search(new_post.features)]
    for similar_post in results:
        if new_post.compare_image(similar_post) >= config.min_similarity:
            reply(new_post, similar_post)
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

                post = NewPost(submission, new_folder)
                print("Checking: {}".format(post.link))

                if post.image_path:
                    check_if_repost(post)

                    # add post to temporary storage so that it may be added to top_posts later
                    storage_folder = os.path.join(new_storage_folder, str(len(os.listdir(new_storage_folder))))
                    post.folder = storage_folder
                    new_posts.append(post)
                    shutil.copy(new_folder, storage_folder)

                shutil.rmtree(new_folder)
                last_post_timestamp = post.date
                
                # update posts when there is low traffic
                if process_start_time.day < datetime.today().day and datetime.today().hour == config.update_hour:
                    print('\n refreshing posts at {0:02d}'.format(datetime.today().hour)
                          + ':{0:02d}'.format(datetime.today().minute))

                    global posts
                    posts = update_posts()
                    process_start_time = datetime.today()

        except prawcore.exceptions.ServerError:
            print("Error occured while connecting to reddit, restarting stream")
            time.sleep(300)

        except Exception as e:
            print("\n\n\nError occured: {}".format(e))
            print("If this isn't an internet connection error please report it "
                  "at https://github.com/Wattsy2020/repost-detector/issues\n\n\n")
            time.sleep(300)

        finally:
            clear_folders()


new_folder = os.path.join(post_recorder.base_folder, 'new')
temp_folder = os.path.join(post_recorder.base_folder, 'temp')
clear_folders()

# used to store new posts so that they can be added to top_posts later
new_storage_folder = os.path.join(post_recorder.base_post_folder, 'new_storage')
if os.path.exists(new_storage_folder):
    shutil.rmtree(new_storage_folder)
os.mkdir(new_storage_folder)

new_posts = []
posts = load_all_posts()

image_searcher = image_search.ImageSearcher(post_recorder.index_file)

if __name__ == '__main__':
    main()
