import os
import sys
import logging 

def setup_logger(log_filepath, debug=False):
    logging_str = "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s"
    log_filepath = os.path.join(os.getcwd(), "logs/seeds/"+log_filepath)
    log_dir = os.path.dirname(log_filepath)  # Extract directory path from log_filepath
    os.makedirs(log_dir, exist_ok=True)  # Create directory if it doesn't exist

    logger = logging.getLogger("Seed logger")
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

# Example Usage:
# logger = setup_logger("seed.log", debug=True)  # Debug mode enabled (prints DEBUG logs)
# logger = setup_logger("seed.log", debug=False)  # Only prints INFO and higher logs
