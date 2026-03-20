import numpy as np
from sklearn.ensemble import IsolationForest

# 🔥 Generate synthetic normal data
np.random.seed(42)

X = np.random.rand(100, 3)  # [risk_score, aqi, traffic]

# Train anomaly model
model = IsolationForest(contamination=0.1)
model.fit(X)


def detect_fraud(risk_score, aqi, traffic):
    data = np.array([[risk_score, aqi / 500, 1 if traffic == "high" else 0]])

    result = model.predict(data)

    if result[0] == -1:
        return True
    return False