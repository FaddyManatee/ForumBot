import logging


logging.basicConfig(filename="bot.log", level=logging.DEBUG, 
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")
_logger = logging.getLogger("BotLog")


async def command_used(user, cmd):
    _logger.info("{} used `/{}`".format(user, cmd))


async def new_threads(count):
    _logger.info("FetchRss found {} new threads".format(count))
