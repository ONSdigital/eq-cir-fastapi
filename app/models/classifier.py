from enum import Enum


class Classifier(Enum):
    FORM_TYPE = "form_type"

    @classmethod
    def valid_classifier(cls, classifier):
        return classifier == Classifier.FORM_TYPE
