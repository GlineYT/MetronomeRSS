import logging

import src.parser.feed_loader as feed_loader
import src.parser.feed_parser as feed_parser
import src.parser.feed_post_processor as feed_post_processor
import src.parser.feed_validator as feed_validator

logger = logging.getLogger(__name__)

def init_pipeline(path):
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

    return ParsedFeed
