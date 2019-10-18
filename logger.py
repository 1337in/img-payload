from colorama import *
from time import gmtime, strftime

_time_format = "%H:%M:%S"

INFO = "INFO"
ERROR = "ERROR"
WARNING = "WARN"
DEBUG = "DEBUG"


def init_logger():
    init(autoreset=True)


def _format_time():
    return strftime(_time_format, gmtime())


def _args_to_str(*msg):
    return "".join([str(x) for x in list(msg[0])])


def log(prefix, level, *msg):
    print(prefix + "(" + _format_time() + ") [" + level + "]: " + _args_to_str(*msg) + Style.RESET_ALL)


def plain_log(*msg):
    print(_args_to_str(*msg))


def info(*msg):
    log("", INFO, msg)


def info_success(*msg):
    log(Fore.GREEN, "SUCCESS", msg)


def info_failure(*msg):
    log(Fore.RED, "FAILURE", msg)


def error(*msg):
    log(Fore.RED + Style.BRIGHT, ERROR, msg)


def warning(*msg):
    log(Fore.YELLOW, WARNING, msg)


def debug(*msg):
    log(Fore.MAGENTA, DEBUG, msg)


def infop(prefix, *msg):
    log(prefix, INFO, msg)


def errorp(prefix, *msg):
    log(prefix, ERROR, msg)


def warningp(prefix, *msg):
    log(prefix, WARNING, msg)


def debugp(prefix, *msg):
    log(prefix, DEBUG, msg)
