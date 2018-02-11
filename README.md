# WordPress Plugin crawler using Scrapy



### Development Environment setup
Developed with Python 3.6.3
```
    $ virtualenv venv -p python3
    $ source venv/bin/activate
    $ pip install -r requirements.txt
```

Notes:
The main.py file was added to help make it easier to interactively debug in pycharm.
The default output format is newline delimited json.

To run:
```
    $ scrapy crawl WordPressPlugins
```
By default output will be stored in: "YYYY-MM-DD.ndjson"

### Export the variables below to save to AWS S3:
```
    $ export AWS_ACCESS_KEY_ID=AKIAXXXXXXXXXXXXXX
    $ export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXX
    $ export AWS_DEFAULT_REGION=XXXXXXXX
    $ export SCRAPY_WORDPRESS_FEED_URI="s3://el-gato-public/scrapy/wordpress-plugins/"`date +%F`".ndjson"
```


Other:
You are also welcome to hit my bucket directly at: s3://el-gato-public/scrapy/wordpress-plugins/*
**** Please be aware that I have enabled requestor pays on the bucket.


If you have any questions feel free to reach out.
