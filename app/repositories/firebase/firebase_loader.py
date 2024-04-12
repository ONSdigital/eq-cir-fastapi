from app.config import settings
from google.cloud.firestore import Client, CollectionReference


class FirebaseLoader:
    def __init__(self):
        self.client = self._connect_client()
        self.ci_collection = self._set_collection("ons-collection-instruments")

    def get_client(self) -> Client:
        """
        Get the firestore client
        """
        return self.client

    def get_ci_collection(self) -> CollectionReference:
        """
        Get the ci collection from firestore
        """
        return self.ci_collection

    def _connect_client(self) -> Client:
        """
        Connect to the firestore client using PROJECT_ID
        """
        if settings.CONF == "unit":
            return None
        return Client(
            project=settings.PROJECT_ID, database=settings.FIRESTORE_DB_NAME
        )

    def _set_collection(self, collection) -> CollectionReference:
        """
        Setup the collection reference for schemas and datasets
        """
        if settings.CONF == "unit":
            return None
        return self.client.collection(collection)


firebase_loader = FirebaseLoader()
