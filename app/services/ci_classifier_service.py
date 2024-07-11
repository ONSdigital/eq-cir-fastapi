import app.exception.exceptions as exceptions
from app.models.classifier import Classifiers


class CiClassifierService:
    @staticmethod
    def get_classifier_type(ci: dict) -> str:
        for key in Classifiers:
            if key.value in ci:
                if ci[key.value] is not None:
                    return key.value
        raise exceptions.ExceptionInvalidClassifier

    @staticmethod
    def get_classifier_value(ci: dict, key: str) -> str:
        return ci[key]

    @staticmethod
    def clean_ci_unused_classifier(ci: dict, classifier_type: str) -> dict:
        for key in Classifiers:
            if key.value != classifier_type:
                ci.pop(key.value, None)
        return ci
