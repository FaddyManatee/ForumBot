import logging


logging.basicConfig(filename="bot.log", level=logging.DEBUG, 
                    format=f"%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s")

_logger = logging.getLogger("BotLog")


async def command_used(user, cmd):
    _logger.info("{} used `/{}`".format(user, cmd))


async def invalid_cookie():
    _logger.error("Invalid cookie! Notified the bot owner to update it")


async def new_threads(count):
    _logger.info("Found {} new threads".format(count))
