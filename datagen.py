import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# --- LOAD YOUR DATA HERE ---
try:
    df = pd.read_csv('disaster_data_2.1.csv')
except FileNotFoundError:
    print("Error: 'disaster_data_2.1.csv' not found. Please make sure the file is in the correct directory or provide the correct path.")
    exit()

# Convert timestamp to datetime and set as index
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.set_index('timestamp')

# --- FEATURE ENGINEERING ---
# Example: Creating a simple lagged feature for gasLevel
df['gasLevel_lagged'] = df['gasLevel'].shift(1)
df = df.fillna(method='bfill') # Corrected fillna

# Define target variable based on detection flags
def get_disaster_type(row):
    if row['floodingDetected'] == 1:
        return 'Flooding'
    elif row['fireDetected'] == 1:
        return 'Fire'
    elif row['gasLeakDetected'] == 1:
        return 'Gas Leak'
    elif row['earthquakeDetected'] == 1:
        return 'Earthquake'
    else:
        return 'No Disaster'

df['disaster_type'] = df.apply(get_disaster_type, axis=1)

# For simplicity, let's focus on detecting disasters and exclude 'No Disaster' for now
df_disaster = df[df['disaster_type'] != 'No Disaster'].copy()

if df_disaster.empty:
    print("No disaster events found in the data based on the detection flags.")
    exit()

# Select features and target for the disaster classification
features = ['accel_x', 'accel_y', 'accel_z', 'gasLevel', 'distanceToWater', 'flowRate', 'earthquakeMagnitude', 'gasLevel_lagged']
target = 'disaster_type'
X = df_disaster[features].fillna(df_disaster[features].mean())
y = df_disaster[target]

# Data preprocessing
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42, stratify=y)

# --- MODEL TRAINING ---
# Train a Random Forest model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# --- MODEL EVALUATION ---
# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# --- CONFUSION MATRIX ---
cm = confusion_matrix(y_test, y_pred)
class_labels = sorted(y.unique()) # Get the unique class labels in order

# Visualize the confusion matrix using seaborn
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_labels, yticklabels=class_labels)
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()