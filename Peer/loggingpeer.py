import os
import sys
import logging 

def setup_logger(log_filepath):
    logging_str = "[%(asctime)s] %(levelname)s - %(message)s"
    log_filepath = os.path.join(os.getcwd(), "logs/peers/"+log_filepath)
    log_dir = os.path.dirname(log_filepath)  # Extract directory path from log_filepath
    os.makedirs(log_dir, exist_ok=True)  # Create directory if it doesn't exist

    logging.basicConfig(
        level=logging.DEBUG,
        format=logging_str,
        handlers=[
            logging.FileHandler(log_filepath),  # Log to the file path provided
            logging.StreamHandler(sys.stdout)    # Log to the console
        ]
    )

    logger = logging.getLogger("Peer logger")
    return logger
