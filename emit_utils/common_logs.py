"""
This code holds some common logging calls, useful to standardize format.

Author: Philip G. Brodrick, philip.brodrick@jpl.nasa.gov
"""

import time
import logging

def logtime():
    """
    Log the current UTC time.
    Args:
        None
    Returns:
        None
    """

    start_time = time.strftime('%Y%m%d_%H%M%S', time.gmtime())

    logging.log(logging.INFO, 'Current UTC time is: {}'.format(start_time))
