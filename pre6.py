import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

# Load and clean data
df = pd.read_csv(r"C:\Users\Santhosh\OneDrive\Desktop\MAJnew\AI_1\disaster_data_2.1.csv") # or use only the csv filename
df_cleaned = df[(df["distanceToWater"] != -1) & (df["distanceToWater"] <= 400) & (df["distanceToWater"] >= 2)][["distanceToWater", "flowRate"]].reset_index(drop=True)

# Feature extraction
window_size = 10
predict_ahead = 26

def build_features(data, target_col, aux_col, window, ahead):
    X, y = [], []
    for i in range(len(data) - window - ahead):
        water = data[target_col].iloc[i:i+window].tolist()
        flow = data[aux_col].iloc[i:i+window].tolist()
        water_diff = [water[j] - water[j-1] for j in range(1, window)]
        flow_diff = [flow[j] - flow[j-1] for j in range(1, window)]
        features = water + flow + water_diff + flow_diff
        label = data[target_col].iloc[i+window+ahead]
        X.append(features)
        y.append(label)
    return np.array(X), np.array(y)

X, y = build_features(df_cleaned, "distanceToWater", "flowRate", window_size, predict_ahead)

# Random split (shuffle = True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=True)

# Scale for Linear Regression
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Models
linreg = LinearRegression()
linreg.fit(X_train_scaled, y_train)
y_pred_lin = linreg.predict(X_test_scaled)

rf = RandomForestRegressor(n_estimators=300, max_depth=15, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)

gbr = GradientBoostingRegressor(n_estimators=300, learning_rate=0.05, max_depth=5, random_state=42)
gbr.fit(X_train, y_train)
y_pred_gbr = gbr.predict(X_test)

xgbr = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=400, max_depth=6, learning_rate=0.05, random_state=42)
xgbr.fit(X_train, y_train)
y_pred_xgb = xgbr.predict(X_test)

# Evaluation
def evaluate(y_true, y_pred, name):
    print(f"\n✅ {name}")
    print(f"  MSE: {mean_squared_error(y_true, y_pred):.2f}")
    print(f"  MAE: {mean_absolute_error(y_true, y_pred):.2f}")
    print(f"  R²: {r2_score(y_true, y_pred):.3f}")

evaluate(y_test, y_pred_lin, "Linear Regression")
evaluate(y_test, y_pred_rf, "Random Forest")
evaluate(y_test, y_pred_gbr, "Gradient Boosting")
evaluate(y_test, y_pred_xgb, "XGBoost")

# Predict current 5-min forecast
latest = df_cleaned.tail(window_size).copy()
latest_water = latest["distanceToWater"].tolist()
latest_flow = latest["flowRate"].tolist()
latest_water_diff = [latest_water[j] - latest_water[j-1] for j in range(1, window_size)]
latest_flow_diff = [latest_flow[j] - latest_flow[j-1] for j in range(1, window_size)]

latest_features = np.array([latest_water + latest_flow + latest_water_diff + latest_flow_diff])
latest_scaled = scaler.transform(latest_features)

print(f"\n📡 5-Min Forecast:")
print(f"  Linear Regression: {linreg.predict(latest_scaled)[0]:.2f} cm")
print(f"  Random Forest:     {rf.predict(latest_features)[0]:.2f} cm")
print(f"  Gradient Boosting: {gbr.predict(latest_features)[0]:.2f} cm")
print(f"  XGBoost:           {xgbr.predict(latest_features)[0]:.2f} cm")

# Plotting actual vs predicted for all models on one page
plt.figure(figsize=(12, 10))

plt.subplot(2, 2, 1)
plt.plot(y_test[:100], label="Actual", color='black')
plt.plot(y_pred_xgb[:100], label="XGBoost", color='blue')
plt.title("XGBoost Prediction vs Actual (First 100 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("Water Level")
plt.legend()
plt.grid(True)

plt.subplot(2, 2, 2)
plt.plot(y_test[:100], label="Actual", color='black')
plt.plot(y_pred_lin[:100], label="Linear Regression", color='red')
plt.title("Linear Regression Prediction vs Actual (First 100 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("Water Level")
plt.legend()
plt.grid(True)

plt.subplot(2, 2, 3)
plt.plot(y_test[:100], label="Actual", color='black')
plt.plot(y_pred_rf[:100], label="Random Forest", color='green')
plt.title("Random Forest Prediction vs Actual (First 100 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("Water Level")
plt.legend()
plt.grid(True)

plt.subplot(2, 2, 4)
plt.plot(y_test[:100], label="Actual", color='black')
plt.plot(y_pred_gbr[:100], label="Gradient Boosting", color='purple')
plt.title("Gradient Boosting Prediction vs Actual (First 100 Samples)")
plt.xlabel("Sample Index")
plt.ylabel("Water Level")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()