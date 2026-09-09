#the pipeline manager for RSS/Atom feeds
import logging

import feed_loader
import feed_parser
import feed_post_processor
import feed_validator

logger = logging.getLogger("__name__")
logging.basicConfig(level=logging.INFO,
format='[%(levelname)s ] %(funcName)s in %(filename)s at %(lineno)d : %(message)s',)

path = "/home/kingmarkoxiv/Desktop/UKTC/other_files/randomcode/python/MetronomeRSS/test/sample-rss-091.xml"

#Load the file
logger.info("Attempting to load example RSS feed")
RSStree,error = feed_loader.loadXML(path)

#Validate the feed type
feedType,valid,error = feed_validator.validateFeedType(RSStree,path)
logger.info(f"Validation finished with returns: ({feedType},{valid!s},{error})")

#Once the feed is known, validate the fields
valid,error = feed_validator.validateFields(RSStree,feedType,path)
logger.info(f"Validation finished with results ({valid},{error})")
#Then parse
ParsedFeed = feed_parser.parsefeed(RSStree,feedType,path)

logger.info("Beggining post processing")
ParsedFeed = feed_post_processor.recursive_unescape(ParsedFeed)
print(f"Processed feed {ParsedFeed}")
