"""
These are the custom exceptions that require
pairing with respective exception handling
functions to be raised properly
"""


class ExceptionNoCIFound(Exception):
    pass


class ExceptionNoCIToDelete(Exception):
    pass


class ExceptionNoCIMetadata(Exception):
    pass


class ExceptionIncorrectKeyNames(Exception):
    pass


class GlobalException(Exception):
    pass


class ValidationException(Exception):
    pass
