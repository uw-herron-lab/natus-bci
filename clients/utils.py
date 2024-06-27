import os
from datetime import datetime
import logging

def get_unique_filename(base_filename):
    """
    Generate a unique filename by appending a counter or timestamp if the file already exists.
    
    Args:
    base_filename (str): The original filename including path.
    
    Returns:
    str: A unique filename.
    """
    directory = os.path.dirname(base_filename)
    filename = os.path.basename(base_filename)
    name, ext = os.path.splitext(filename)
    
    # First, try with a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = os.path.join(directory, f"{name}_{timestamp}{ext}")
    
    # If timestamp version already exists (unlikely but possible), use a counter
    counter = 1
    while os.path.exists(unique_filename):
        unique_filename = os.path.join(directory, f"{name}_{timestamp}_{counter}{ext}")
        counter += 1
    
    return unique_filename

# Configure logging
def setup_logging(log_file_base: str, log_level=logging.INFO) -> None:
    unique_log_file = get_unique_filename(log_file_base)
    logging.basicConfig(
        filename=unique_log_file,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )