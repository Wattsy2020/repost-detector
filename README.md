A Reddit bot that uses a Content based image retrieval engine to detect when new posts to a subreddit have already been posted.

## Built with
* [Praw](https://praw.readthedocs.io/en/latest/) - A wrapper for Reddit's API. Used to retrieve new submissions and post replies.
* [Psaw](https://github.com/dmarx/psaw) - A wrapper for the PushShift Reddit API, which allows access to older posts that Reddit's API restricts. Used to download older posts. 
* [OpenCV](https://opencv.org/) - The standard computer vision library. Used to build the image retrieval engine
* [scikit-image](http://scikit-image.org/) - An image processing library. Used to compare the structural similarity of images.

Currently in development
