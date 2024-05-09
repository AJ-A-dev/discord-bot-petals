
import logging

# create loger for general info
general_logger = logging.getLogger("general")
general_logger.setLevel(logging.INFO)

# create logger for performance tracking
performance_logger = logging.getLogger("performance")
performance_logger.setLevel(logging.INFO)


# Configure the handler for the general logger
general_handler = logging.FileHandler('data/general.log')
general_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
general_logger.addHandler(general_handler)

# Configure the handler for the performance logger
performance_handler = logging.FileHandler('data/performance.log')
performance_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
performance_logger.addHandler(performance_handler)

logging.basicConfig(filename='data/general.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    performance_logger.info("hello %s", 23)
    general_logger.info("hello %s", 10)
