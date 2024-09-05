import logging
import datetime
import time

class RateLimitingFilter(logging.Filter):
    """logging filter to throttle log records generation."""

    def __init__(
        self,
        count: int,
        per: datetime.timedelta,
        burst: int = 100,
    ):
        """Instantiate a rate limiting filter

        Args:
            count (int): Number of log records to allow in given `per` time frame.
            per (datetime.timedelta): Time frame where you allow at most `count` log records.
            burst (int, optional): Number of records allowed during start burst. Defaults to 100.
        """
        super().__init__()
        self._count = count
        self._per = per
        self._burst = burst

        self._allowance = burst
        self._last_check = time.monotonic()
        self.throttled = 0

    def _consume(self):
        """Consume a publication token if possible

        :return:
            True if a token has been consumed
        """
        now = time.monotonic()
        delta = now - self._last_check
        self._last_check = now

        refilled_tokens = delta * (self._count / self._per.total_seconds())
        self._allowance = min(self._burst, self._allowance + refilled_tokens)
        print(self._allowance)

        if self._allowance < 1:
            return False

        self._allowance -= 1
        return True

    def filter(self, record):
        """Filters-out record if rate limits are reached.

        Count the number of records filtered, to report it in the next unfiltered record.
        """
        if not self._consume():
            self.throttled += 1
            return False

        if self.throttled > 0:
            record.msg += f" ({self.throttled} additional messages suppressed!)"
        self.throttled = 0
        return True
