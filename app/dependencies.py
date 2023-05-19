import logging
from typing import Annotated

from fastapi import Depends

from app.config import get_app_logger

Logger = Annotated[logging.Logger, Depends(get_app_logger)]
