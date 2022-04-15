from colorama import Fore, Back
import time

def _get_time() -> str:
    month = time.strftime("%m")
    day = time.strftime("%d")
    year = time.strftime("%Y")
    hour = time.strftime("%H")
    minute = time.strftime("%M")
    second = time.strftime("%S")
    return f"{month}-{day}-{year} {hour}-{minute}-{second}"

class LogType:
    prefix = None        

class LogError(LogType):
    prefix =           f"{Back.RED}{Fore.WHITE} | ERROR   {Back.LIGHTBLACK_EX}{Fore.WHITE} {_get_time()} {Back.RED} {Back.RESET}"

class LogInfo(LogType):
    prefix =         f"{Back.GREEN}{Fore.WHITE} | INFO    {Back.LIGHTBLACK_EX}{Fore.WHITE} {_get_time()} {Back.LIGHTGREEN_EX} {Back.RESET}"

class LogWarning(LogType):
    prefix =        f"{Back.YELLOW}{Fore.WHITE} | WARNING {Back.LIGHTBLACK_EX}{Fore.WHITE} {_get_time()} {Back.YELLOW} {Back.RESET}"

def print_log(msg: str, log_type: LogType) -> None:
    """Print something into the console.
    
    Parameters:
        msg (str): The log message.
        type (LogType): The log type. The following are available: LogError, LogInfo, LogWarning.
    
    """
    print(f"{log_type.prefix} {msg}")
