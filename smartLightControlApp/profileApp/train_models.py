import io

import joblib
import pandas as pd
import xgboost as xgb
from django.core.exceptions import ObjectDoesNotExist
from listenerApp.models import LightingEvent, ModelsStorage
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, \
    mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler


def train_and_save_models(user):
    # Load data from Django model
    queryset = LightingEvent.objects.filter(user=user).values()
    df = pd.DataFrame(list(queryset))

    # Handle missing values
    df.ffill(inplace=True)

    # Convert timestamp to datetime and create additional time-based features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['minute'] = df['timestamp'].dt.minute
    df['second'] = df['timestamp'].dt.second
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['part_of_day'] = df['hour'] // 6  # Divides the day into 4 parts

    # Feature engineering: previous state and brightness
    df['prev_state'] = df['state'].shift(1).fillna(0)
    df['prev_brightness'] = df['brightness'].shift(1).fillna(df['brightness'].mean())
    df['prev_color_r'] = df['color_r'].shift(1).fillna(df['color_r'].mean())
    df['prev_color_g'] = df['color_g'].shift(1).fillna(df['color_g'].mean())
    df['prev_color_b'] = df['color_b'].shift(1).fillna(df['color_b'].mean())
    df['prev_state_duration'] = (df['timestamp'] - df['timestamp'].shift(1)).fillna(
        pd.Timedelta(seconds=0)).dt.total_seconds()

    # Split features and target
    X = df[['hour', 'minute', 'second', 'day_of_week', 'part_of_day', 'lamp_id', 'prev_state', 'prev_brightness',
            'prev_color_r', 'prev_color_g', 'prev_color_b', 'prev_state_duration']]
    y_state = df['state']
    y_brightness = df['brightness']
    y_color_r = df['color_r']
    y_color_g = df['color_g']
    y_color_b = df['color_b']

    # One-hot encode categorical variables
    X = pd.get_dummies(X, columns=['lamp_id', 'part_of_day'], drop_first=True)

    # Handle missing target values by filling or dropping
    y_brightness.fillna(y_brightness.mean(), inplace=True)
    y_color_r.fillna(y_color_r.mean(), inplace=True)
    y_color_g.fillna(y_color_g.mean(), inplace=True)
    y_color_b.fillna(y_color_b.mean(), inplace=True)

    # Split into training and testing sets
    X_train, X_test, y_state_train, y_state_test = train_test_split(X, y_state, test_size=0.2, random_state=42)
    _, _, y_brightness_train, y_brightness_test = train_test_split(X, y_brightness, test_size=0.2, random_state=42)
    _, _, y_color_r_train, y_color_r_test = train_test_split(X, y_color_r, test_size=0.2, random_state=42)
    _, _, y_color_g_train, y_color_g_test = train_test_split(X, y_color_g, test_size=0.2, random_state=42)
    _, _, y_color_b_train, y_color_b_test = train_test_split(X, y_color_b, test_size=0.2, random_state=42)

    # Scale the features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Hyperparameter tuning for state model using XGBoost
    param_grid = {
        'n_estimators': [100, 200, 300],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.2],
        'subsample': [0.7, 0.8, 0.9],
        'colsample_bytree': [0.7, 0.8, 0.9]
    }

    xgb_model = xgb.XGBClassifier(random_state=42)
    grid_search = RandomizedSearchCV(estimator=xgb_model, param_distributions=param_grid, n_iter=50, cv=5, n_jobs=-1,
                                     verbose=2, random_state=42)
    grid_search.fit(X_train, y_state_train)
    best_state_model = grid_search.best_estimator_

    # Train other models without hyperparameter tuning for simplicity
    brightness_model = RandomForestRegressor(random_state=42)
    color_r_model = RandomForestRegressor(random_state=42)
    color_g_model = RandomForestRegressor(random_state=42)
    color_b_model = RandomForestRegressor(random_state=42)

    brightness_model.fit(X_train, y_brightness_train)
    color_r_model.fit(X_train, y_color_r_train)
    color_g_model.fit(X_train, y_color_g_train)
    color_b_model.fit(X_train, y_color_b_train)

    # Save models to the database
    scaler_bytes = io.BytesIO()
    joblib.dump(scaler, scaler_bytes)
    scaler_bytes.seek(0)

    state_model_bytes = io.BytesIO()
    joblib.dump(best_state_model, state_model_bytes)
    state_model_bytes.seek(0)

    brightness_model_bytes = io.BytesIO()
    joblib.dump(brightness_model, brightness_model_bytes)
    brightness_model_bytes.seek(0)

    color_r_model_bytes = io.BytesIO()
    joblib.dump(color_r_model, color_r_model_bytes)
    color_r_model_bytes.seek(0)

    color_g_model_bytes = io.BytesIO()
    joblib.dump(color_g_model, color_g_model_bytes)
    color_g_model_bytes.seek(0)

    color_b_model_bytes = io.BytesIO()
    joblib.dump(color_b_model, color_b_model_bytes)
    color_b_model_bytes.seek(0)

    try:
        models_storage = ModelsStorage.objects.get(user=user)
    except ObjectDoesNotExist:
        models_storage = ModelsStorage(user=user)

    models_storage.scaler = scaler_bytes.getvalue()
    models_storage.state_model = state_model_bytes.getvalue()
    models_storage.brightness_model = brightness_model_bytes.getvalue()
    models_storage.color_r_model = color_r_model_bytes.getvalue()
    models_storage.color_g_model = color_g_model_bytes.getvalue()
    models_storage.color_b_model = color_b_model_bytes.getvalue()
    models_storage.save()

    # Evaluate the models
    y_state_pred = best_state_model.predict(X_test)
    accuracy = accuracy_score(y_state_test, y_state_pred)
    precision = precision_score(y_state_test, y_state_pred)
    recall = recall_score(y_state_test, y_state_pred)
    f1 = f1_score(y_state_test, y_state_pred)

    print(f"State Prediction - Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1-score: {f1}")

    y_brightness_pred = brightness_model.predict(X_test)
    y_color_r_pred = color_r_model.predict(X_test)
    y_color_g_pred = color_g_model.predict(X_test)
    y_color_b_pred = color_b_model.predict(X_test)

    brightness_mae = mean_absolute_error(y_brightness_test, y_brightness_pred)
    brightness_mse = mean_squared_error(y_brightness_test, y_brightness_pred)
    brightness_r2 = r2_score(y_brightness_test, y_brightness_pred)
    print(f"Brightness Prediction - MAE: {brightness_mae}, MSE: {brightness_mse}, R2: {brightness_r2}")

    color_r_mae = mean_absolute_error(y_color_r_test, y_color_r_pred)
    color_r_mse = mean_squared_error(y_color_r_test, y_color_r_pred)
    color_r_r2 = r2_score(y_color_r_test, y_color_r_pred)
    print(f"Color R Prediction - MAE: {color_r_mae}, MSE: {color_r_mse}, R2: {color_r_r2}")

    color_g_mae = mean_absolute_error(y_color_g_test, y_color_g_pred)
    color_g_mse = mean_squared_error(y_color_g_test, y_color_g_pred)
    color_g_r2 = r2_score(y_color_g_test, y_color_g_pred)
    print(f"Color G Prediction - MAE: {color_g_mae}, MSE: {color_g_mse}, R2: {color_g_r2}")

    color_b_mae = mean_absolute_error(y_color_b_test, y_color_b_pred)
    color_b_mse = mean_squared_error(y_color_b_test, y_color_b_pred)
    color_b_r2 = r2_score(y_color_b_test, y_color_b_pred)
    print(f"Color B Prediction - MAE: {color_b_mae}, MSE: {color_b_mse}, R2: {color_b_r2}")
