import datetime

import pytest

from app.services.datetime_service import DatetimeService


@pytest.mark.use_real_datetime
def test_get_current_date_and_time():
    """
    Test that the get_current_date_and_time function returns a datetime object with UTC timezone.
    """
    dt = DatetimeService.get_current_date_and_time()

    assert dt.tzinfo is not None
    assert dt.tzinfo.utcoffset(dt) == datetime.timedelta(0)
    assert dt.tzname() in {"UTC", "UTC+00:00"}
