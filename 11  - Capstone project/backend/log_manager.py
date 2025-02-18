import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def info_log(message):
    logging.info(message)

def error_log(message):
    logging.error(message)