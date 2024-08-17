from datetime import datetime, timedelta

# Given date and time
given_date = datetime(2024, 9, 1, 20, 44)

# Subtract 92 days
date_92_days_ago = given_date - timedelta(days=92)

# Print the result
print("The date exactly 92 days before", given_date.strftime("%B %d, %Y at %H:%M"), "is", date_92_days_ago.strftime("%B %d, %Y at %H:%M"))
