import io
import joblib
import pandas as pd
from django.contrib.auth.models import User
from .models import ModelsStorage, LightingEvent

def predict(data, user):
    models_storage = ModelsStorage.objects.get(user=user)

    scaler = joblib.load(io.BytesIO(models_storage.scaler))
    model_columns = models_storage.model_columns

    df = pd.DataFrame([data])
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
    df['prev_timestamp'] = pd.to_datetime(df['prev_timestamp']).dt.tz_localize(None)
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['second'] = df['timestamp'].dt.second
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['part_of_day'] = df['hour'] // 6
    df['prev_state_duration'] = (df['timestamp'] - df['prev_timestamp']).dt.total_seconds()

    # One-hot encode categorical variables
    df = pd.get_dummies(df, columns=['lamp_id', 'part_of_day'], drop_first=True)

    # Ensure all expected columns are present
    for col in model_columns:
        if col not in df.columns:
            df[col] = 0

    # Reorder columns to match training order
    df = df[model_columns]

    # Scale the features
    processed_data = scaler.transform(df)

    state_model = joblib.load(io.BytesIO(models_storage.state_model))
    brightness_model = joblib.load(io.BytesIO(models_storage.brightness_model))
    color_r_model = joblib.load(io.BytesIO(models_storage.color_r_model))
    color_g_model = joblib.load(io.BytesIO(models_storage.color_g_model))
    color_b_model = joblib.load(io.BytesIO(models_storage.color_b_model))

    state_pred = state_model.predict(processed_data)
    brightness_pred = brightness_model.predict(processed_data)
    color_r_pred = color_r_model.predict(processed_data)
    color_g_pred = color_g_model.predict(processed_data)
    color_b_pred = color_b_model.predict(processed_data)

    return {
        'state': state_pred[0],
        'brightness': brightness_pred[0] if state_pred[0] else None,
        'color_r': color_r_pred[0] if state_pred[0] else None,
        'color_g': color_g_pred[0] if state_pred[0] else None,
        'color_b': color_b_pred[0] if state_pred[0] else None
    }


def ai_control(user):
    from controllers.controller import Controller
    from controllers.lamp import Lamp

    controller = Controller(token=user.userprofile.access_token, domain=user.userprofile.company_domain)
    recent_predictions = {lamp_id: [] for lamp_id in ['light.virtual_light', 'light.virtual_light1']}

    while user.userprofile.ai_control_enabled:
        user = User.objects.get(id=user.id)
        if not user.userprofile.ai_control_enabled:
            break

        lights = controller.get_light_entities()
        for light in lights:
            last_light_event = LightingEvent.objects.filter(user=user, lamp_id=light['entity_id']).order_by(
                '-timestamp').first()
            lamp_controller = Lamp(entity_id=light['entity_id'], token=user.userprofile.access_token,
                                   domain=user.userprofile.company_domain)

            data = {
                'timestamp': pd.to_datetime('now').tz_localize(None),
                'lamp_id': last_light_event.lamp_id,
                'prev_timestamp': pd.to_datetime(last_light_event.timestamp).tz_localize(None),
                'prev_state': last_light_event.state,
                'prev_brightness': last_light_event.brightness,
                'prev_color_r': last_light_event.color_r,
                'prev_color_g': last_light_event.color_g,
                'prev_color_b': last_light_event.color_b
            }

            prediction = predict(data, user)

            # Use recent history to stabilize the predictions
            recent_states = recent_predictions[light['entity_id']]
            recent_states.append(prediction['state'])

            # Only consider the last 5 predictions to avoid frequent changes
            if len(recent_states) > 5:
                recent_states.pop(0)

            # Decide the final state based on the majority of recent predictions
            final_state = max(set(recent_states), key=recent_states.count)

            if final_state:
                current_brightness = prediction['brightness']
                lamp_controller.change_brightness(current_brightness)

                current_color_r = prediction['color_r']
                current_color_g = prediction['color_g']
                current_color_b = prediction['color_b']
                lamp_controller.change_color([current_color_r, current_color_g, current_color_b])

                new_light_event = LightingEvent(user=user, state=final_state, lamp_id=data['lamp_id'],
                                                brightness=current_brightness, color_r=current_color_r,
                                                color_g=current_color_g, color_b=current_color_b,
                                                timestamp=data['timestamp'])
                print(
                    f"\n{data['timestamp']}  {data['lamp_id']} - state:{final_state} - brightness:{current_brightness} - color:{current_color_r} - {current_color_g} - {current_color_b}")

            else:
                lamp_controller.change_state(False)

                new_light_event = LightingEvent(user=user, lamp_id=data['lamp_id'], state=final_state,
                                                timestamp=data['timestamp'])

                print(f"\n{data['timestamp']}  {data['lamp_id']} - state:{final_state})")

            new_light_event.save()