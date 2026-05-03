from enum import Enum


class ConsoleKey(str, Enum):
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    INFO = "info"
    START = "start"
    FINISH = "finish"
