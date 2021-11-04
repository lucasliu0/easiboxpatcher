import logging

class EasiLogging():

    def setLevel(level=None):
        logging.basicConfig(level= level)

    def info(message):
        logging.info(message)

    def debug(message):
        logging.debug(message)
        
    def error(message):
        logging.error(message)
        
    def warning(message):
        logging.warning(message)

    def critical(message):
        logging.critical(message)

    def debugc(state, message):
        if state == 1:
            logging.debug(message)

