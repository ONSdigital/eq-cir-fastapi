"""
These are the custom exceptions that require
pairing with respective exception handling
functions to be raised properly
"""


class ExceptionIncorrectSchemaKey(Exception):
    pass


class ExceptionIncorrectSchemaV2Key(Exception):
    pass


class ExceptionNoSchemaMetadataCollection(Exception):
    pass


class ExceptionNoSchemaFound(Exception):
    pass


class ExceptionIncorrectDatasetKey(Exception):
    pass


class ExceptionNoDatasetMetadata(Exception):
    pass


class ExceptionNoUnitData(Exception):
    pass


class GlobalException(Exception):
    pass


class ValidationException(Exception):
    pass


class ExceptionNoSurveyIDs(Exception):
    pass
