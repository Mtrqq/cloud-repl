import enum


class Period(enum.Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"

    def as_seconds(self: "Period") -> int:
        seconds = {
            Period.MINUTE: 60,
            Period.HOUR: 60 * 60,
            Period.DAY: 60 * 60 * 24,
            Period.WEEK: 60 * 60 * 24 * 7,
        }.get(self)

        if seconds is None:
            raise ValueError(f"Invalid period value provided ({self})")

        return seconds
