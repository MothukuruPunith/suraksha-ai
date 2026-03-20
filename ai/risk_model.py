import numpy as np
from sklearn.linear_model import LinearRegression

# 🔥 Generate synthetic dataset
np.random.seed(42)

num_samples = 100

weather = np.random.randint(0, 3, num_samples)  # 0 clear, 1 rain, 2 storm
aqi = np.random.randint(50, 400, num_samples)
traffic = np.random.randint(0, 2, num_samples)

X = np.column_stack((weather, aqi, traffic))

# 🔥 Simulated risk logic
y = (0.2 * weather + 0.003 * aqi + 0.2 * traffic) + np.random.rand(num_samples) * 0.1
y = np.clip(y, 0, 1)

# 🔥 Train model
model = LinearRegression()
model.fit(X, y)


def encode_inputs(weather, aqi, traffic):
    weather_map = {"clear": 0, "rain": 1, "storm": 2}
    traffic_map = {"low": 0, "high": 1}

    return np.array([[weather_map[weather], aqi, traffic_map[traffic]]])


def calculate_risk(weather, aqi, traffic):
    input_data = encode_inputs(weather, aqi, traffic)
    prediction = model.predict(input_data)[0]

    return round(max(0, min(prediction, 1)), 2)


def calculate_premium(risk_score):
    base_price = 20
    dynamic_factor = 60

    return round(base_price + (risk_score * dynamic_factor), 2)