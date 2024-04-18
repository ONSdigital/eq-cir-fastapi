import uuid


class CreateGuidService:
    @staticmethod
    def create_guid() -> str:
        return str(uuid.uuid4())
