from datetime import datetime


class DatetimeService:
    @staticmethod
    def get_current_date_and_time() -> datetime:
        """
        Gets current date and time. Wrapper for datetime.now() function to make it easier to mock for tests.
        """
        return datetime.now()
