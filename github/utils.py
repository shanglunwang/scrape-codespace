from datetime import datetime, timezone
import pytz


def get_current_gmt9():
    # Get current time in UTC
    current_time_utc = datetime.now(timezone.utc)

    # Convert to GMT+9
    gmt_plus_9 = pytz.timezone("Asia/Tokyo")  # GMT+9 timezone
    current_time_gmt_plus_9 = current_time_utc.astimezone(gmt_plus_9)

    # Format as string in the desired format
    current_time_str = current_time_gmt_plus_9.strftime("%Y%m%d%H%M")

    return current_time_str
