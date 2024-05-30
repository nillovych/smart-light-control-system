import random
from datetime import datetime, timedelta
from listenerApp.models import LightingEvent
from django.contrib.auth.models import User

# Parameters for data generation
start_date = datetime(2024, 3, 27, 10, 0)  # Start period
end_date = datetime(2024, 5, 27, 10, 0)  # End period
lamp_ids = ['light.virtual_light', 'light.virtual_light1']  # List of lamp IDs
user = User.objects.first()  # Use the first user for all records

# Generation of random values for each lamp over the entire period
current_time = start_date
time_step = timedelta(minutes=10)

data = []
count = 0

while current_time < end_date:
    for lamp_id in lamp_ids:
        # Simulate realistic light usage patterns
        hour = current_time.hour
        day_of_week = current_time.weekday()

        # Determine if the light should be on based on realistic daily routines
        if day_of_week < 5:  # Weekdays
            if 6 <= hour < 8 or 18 <= hour < 23:  # More likely to be on during morning and evening
                state = random.choices([True, False], [0.8, 0.2])[0]
            elif 8 <= hour < 18:  # Less likely to be on during work hours
                state = random.choices([True, False], [0.2, 0.8])[0]
            else:  # Early morning or late night
                state = random.choices([True, False], [0.1, 0.9])[0]
        else:  # Weekends
            if 8 <= hour < 10 or 18 <= hour < 24:  # More likely to be on during breakfast and evening
                state = random.choices([True, False], [0.7, 0.3])[0]
            elif 10 <= hour < 18:  # On during the day, but less likely
                state = random.choices([True, False], [0.4, 0.6])[0]
            else:  # Early morning or late night
                state = random.choices([True, False], [0.1, 0.9])[0]

        if state:
            # Higher brightness during evening, lower in the morning
            if 18 <= hour < 23:
                brightness = random.randint(200, 255)
            elif 6 <= hour < 8:
                brightness = random.randint(150, 200)
            else:
                brightness = random.randint(100, 200)

            color_r = random.randint(100, 255)
            color_g = random.randint(100, 255)
            color_b = random.randint(100, 255)

            event = LightingEvent(
                user=user,
                timestamp=current_time,
                lamp_id=lamp_id,
                brightness=brightness,
                color_r=color_r,
                color_g=color_g,
                color_b=color_b,
                state=state
            )
        else:
            event = LightingEvent(
                user=user,
                timestamp=current_time,
                lamp_id=lamp_id,
                state=state
            )
        data.append(event)
        count += 1
        print(f"Event #{count} created for {lamp_id}")
    current_time += time_step

print(f"Created {len(data)} lighting events.")

LightingEvent.objects.bulk_create(data)
print("Data population complete.")
