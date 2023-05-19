LOGGER_DEBUG_FORMAT: str = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "[PID %(process)d] "
    "[Thread %(thread)d] "
    "[%(filename)s.%(lineno)s -> %(funcName)s()] "
    "%(message)s"
)

LOGGER_FORMAT: str = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[%(name)s] "
    "[%(filename)s.%(lineno)s -> %(funcName)s()] "
    "%(message)s"
)
