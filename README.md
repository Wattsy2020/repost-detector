A Reddit bot that uses a Content based image retrieval engine to detect when new posts to a subreddit have already been posted.

## How it works
1. The bot downloads popular posts from a subreddit and stores them for future reference
2. The bot loads it's stored posts into memory so they can be searched
3. When a new post to the subreddit is made the bot uses an image search engine to find similar posts, if there are any matches it posts a reply. 

## How to setup this bot on another subreddit
1. Install python from [here](https://www.python.org/downloads/)
2. Open a cmd prompt and type the following commands to download all the modules the program needs:
      * pip install requests
      * pip install numpy
      * pip install opencv-python
      * pip install praw
      * pip install psaw
      * pip install requests
      * pip install scikit-image
      * pip install urllib3
3. Download all the code from the source directory
4. Rename config-example.py to config.py then open it in a text editor to change the settings.
   Most of these are self explanatory but here are some pointers:
   
      * To fill out the reddit settings you'll need to make a bot account, then follow [these](http://pythonforengineers.com/build-a-reddit-bot-part-1/) instructions to fill out the client_id and client_secret variables, finally name the user_agent whatever you want.
      * update_hour needs to be set to the lowest traffic time otherwise it'll miss some popular posts
      * The only change you could make to min_similarity is to increase it a bit, it definetely shouldn't go any lower
      * If you're setting this up for a really large subreddit (bigger then prequelmemes) change colour_bins to \[10, 12, 10\]
      * Leave the line at the bottom of the message in so I can get feedback on the bot
5. Download the posts from your subreddit by running setup.py (double click on it)
6. Once setup.py says it is done you're ready to finally run the bot; Simply run main.py and the bot will start.
      

## Built with
* [Praw](https://praw.readthedocs.io/en/latest/) - A wrapper for Reddit's API. Used to retrieve new submissions and post replies.
* [Psaw](https://github.com/dmarx/psaw) - A wrapper for the PushShift Reddit API, which allows access to older posts that Reddit's API restricts. Used to download older posts. 
* [OpenCV](https://opencv.org/) - The standard computer vision library. Used to build the image retrieval engine
* [scikit-image](http://scikit-image.org/) - An image processing library. Used to compare the structural similarity of images.

## What each module does
* image_search - contains classes for classifying images and searching for images with similar classification
* post_recorder - contains methods for downloading posts using both APIs
* post_comparison - contains classes to represent reddit posts and a method to compare two images
* main.py - uses all the modules to run the bot
* tests.py - runs assorted tests
* config.py - stores the settings the bot uses
* setup.py - uses post_recorder to create the archive of reddit posts

## To do
* Write documentation, add docstrings to methods etc...
* Write a better reply message
* Make it easier to install the bot
