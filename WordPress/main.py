#https://stackoverflow.com/questions/21788939/how-to-use-pycharm-to-debug-scrapy-projects

from scrapy import cmdline
cmdline.execute("scrapy crawl WordPressPlugins".split())
