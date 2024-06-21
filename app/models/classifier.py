from enum import StrEnum


class Classifiers(StrEnum):
    FORM_TYPE = "form_type"
    DEFAULT_CLASSIFIER = "default"

    @classmethod
    def has_member_key(cls, key):
        if key in cls:
            return True
