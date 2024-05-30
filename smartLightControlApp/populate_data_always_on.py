import random
from datetime import datetime, timedelta
from listenerApp.models import LightingEvent
from django.contrib.auth.models import User

# Parameters for data generation
start_date = datetime(2024, 3, 27, 10, 0)  # Start period
end_date = datetime(2024, 5, 27, 10, 0)  # End period
lamp_ids = ['light.virtual_light', 'light.virtual_light1']  # List of lamp IDs
user = User.objects.filter(username='roma').first()  # Use the user with username 'taya' for all records

# Generation of random values for each lamp over the entire period
current_time = start_date
time_step = timedelta(minutes=10)  # Predict every 10 minutes

data = []
count = 0
previous_state = {lamp_id: False for lamp_id in lamp_ids}

while current_time < end_date:
    for lamp_id in lamp_ids:
        # Simulate realistic light usage patterns
        hour = current_time.hour

        # Determine if the light should be on based on realistic daily routines
        if 8 <= hour < 20:  # More likely to be on between 8 AM and 8 PM
            state = random.choices([True, False], [0.8, 0.2])[0]
        else:  # Less likely to be on outside this range
            state = random.choices([True, False], [0.2, 0.8])[0]

        # Ensure state does not change too frequently by considering previous state
        if previous_state[lamp_id] and not state:
            if random.random() > 0.2:  # 80% chance to remain on if it was on before
                state = True
        elif not previous_state[lamp_id] and state:
            if random.random() > 0.8:  # 80% chance to remain off if it was off before
                state = False

        previous_state[lamp_id] = state

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

    # Advance the time by a fixed interval of 10 seconds
    current_time += time_step

print(f"Created {len(data)} lighting events.")

LightingEvent.objects.bulk_create(data)
print("Data population complete.")
