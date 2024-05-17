"""
These are the custom exceptions that require
pairing with respective exception handling
functions to be raised properly
"""


class ExceptionIncorrectSchemaKey(Exception):
    pass


class ExceptionIncorrectSchemaV2Key(Exception):
    pass


class ExceptionNoCIMetadataCollection(Exception):
    pass


class ExceptionNoCIFound(Exception):
    pass


class ExceptionNoCIMetadata(Exception):
    pass


class GlobalException(Exception):
    pass


class ValidationException(Exception):
    pass


class ExceptionNoSurveyIDs(Exception):
    pass
