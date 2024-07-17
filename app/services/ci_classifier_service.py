import app.exception.exceptions as exceptions
from app.models.classifier import Classifiers


class CiClassifierService:
    @staticmethod
    def get_classifier_type(ci: dict) -> str:
        """
        This method fetch the classifier type from the ci dictionary
        Throw exception if no classifier type can be found

        Parameters:
        ci: The ci dictionary

        Returns:
        The classifier type found
        """
        for key in Classifiers:
            if key.value in ci:
                if ci[key.value] is not None:
                    return key.value
        raise exceptions.ExceptionInvalidClassifier

    @staticmethod
    def get_classifier_value(ci: dict, key: str) -> str:
        """
        This method get the classifier value from the ci dictionary

        Parameters:
        ci: The ci dictionary
        key: The classifier type

        Returns:
        The classifier value
        """
        return ci[key]

    @staticmethod
    def clean_ci_unused_classifier(ci: dict, classifier_type: str) -> dict:
        """
        This method remove unused classifier from the ci dictionary
        FastAPI pydantic model will auto create the specified optional classifier
        fields with None value if not provided. This method will remove those fields

        Parameters:
        ci: The ci dictionary
        classifier_type: The classifier type that is used

        Returns:
        The cleaned ci dictionary
        """
        for key in Classifiers:
            if key.value != classifier_type:
                ci.pop(key.value, None)
        return ci
