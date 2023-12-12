import logging

from .filemanager import FileManager

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())