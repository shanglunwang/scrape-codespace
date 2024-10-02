from datetime import datetime, timezone
import pytz


def get_current_gmt9():
    # Get current time in UTC
    current_time_utc = datetime.now(timezone.utc)

    # Convert to GMT+9
    gmt_plus_9 = pytz.timezone("Asia/Tokyo")  # GMT+9 timezone
    current_time_gmt_plus_9 = current_time_utc.astimezone(gmt_plus_9)

    # Format as string
    current_time_str = current_time_gmt_plus_9.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Parse the string back to a datetime object
    parsed_time = datetime.strptime(current_time_str, "%Y-%m-%dT%H:%M:%SZ")

    return parsed_time
