from django.utils import timezone


def generate_unique_filepath(filename):
    current_timestamp = timezone.now()
    date = current_timestamp.strftime("%Y/%m/%d")
    return f"{date}/{current_timestamp.timestamp()}_{filename}"
