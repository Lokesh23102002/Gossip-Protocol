import os
import sys
import logging 

def setup_logger(log_filepath, debug=False):
    logging_str = "[%(asctime)s] %(levelname)s - %(message)s"
    log_filepath = os.path.join(os.getcwd(), "logs/peers/"+log_filepath)
    log_dir = os.path.dirname(log_filepath)  # Extract directory path from log_filepath
    os.makedirs(log_dir, exist_ok=True)  # Create directory if it doesn't exist

    logger = logging.getLogger("Peer logger")
    logger.setLevel(logging.DEBUG)  # Always log everything to file

    # File handler (Logs everything)
    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging.DEBUG)  # Log everything to file
    file_handler.setFormatter(logging.Formatter(logging_str))

    # Console handler (Logs INFO by default, DEBUG if debug=True)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)  # Debug mode toggle
    console_handler.setFormatter(logging.Formatter(logging_str))

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


