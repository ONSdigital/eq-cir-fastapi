from datetime import datetime, timezone


class DatetimeService:
    @staticmethod
    def get_current_date_and_time() -> datetime:
        """
        Gets current date and time in UTC timezone.
        """
        return datetime.now(tz=timezone.utc)
