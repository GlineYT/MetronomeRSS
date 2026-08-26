#the pipeline manager for RSS/Atom feeds
import feedLoader
import feedValidator
import feedParser
import feedPostProcessor
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger("main")
logging.basicConfig(level=logging.INFO,
format='[%(levelname)s ] %(funcName)s in %(filename)s at %(lineno)d : %(message)s',)

path = "/home/kingmarkoxiv/Desktop/UKTC/other_files/randomcode/python/MetronomeRSS/test/entity-test-heavy.xml"

#Load the file
logging.info("Attempting to load example RSS feed")
RSStree,error = feedLoader.loadXML(path)

#Validate the feed type
feedType,valid,error = feedValidator.validateFeedType(RSStree,path)
logging.info(f"Validation finished with returns: ({feedType},{str(valid)},{error})")

#Once the feed is known, validate the fields
valid,error = feedValidator.validateFields(RSStree,feedType,path)

#Then parse
ParsedFeed = feedParser.parsefeed(RSStree,feedType,path)

logging.info("Beggining post processing")
ParsedFeed = feedPostProcessor.recursive_unescape(ParsedFeed)
print(f"Processed feed {ParsedFeed}")
