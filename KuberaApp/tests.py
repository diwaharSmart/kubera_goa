import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Data Collection and Preparation
years = ['1998', '1999']  # Adjust these to your available data
data = []

for year in years:
    sheet_name = year
    df = pd.read_excel('path_to_your_excel_file.xlsx', sheet_name=sheet_name)
    data.append(df)

# Combine data from all years into a single DataFrame
combined_data = pd.concat(data, ignore_index=True)

# Organize the data
combined_data.to_csv('organized_lottery_data.csv', index=False)

# Data Preprocessing
combined_data['Date'] = pd.to_datetime(combined_data['Date'])
combined_data['Days'] = (combined_data['Date'] - combined_data['Date'].min()).dt.days

# Normalize the data (optional)
# You can scale the 'Days' column to a specific range if needed

# Feature Engineering
combined_data['Month'] = combined_data['Date'].dt.month
# You can add more features like day of the week, lag features, etc.

# Model Selection and Training
features = ['Days', 'Month']  # Adjust features based on your needs
target = 'LastThreeDigits'
X = combined_data[features]
y = combined_data[target]

# Split data into training and validation sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the model
model = LinearRegression()
model.fit(X_train, y_train)

# Model Evaluation
val_predictions = model.predict(X_val)
rmse = mean_squared_error(y_val, val_predictions, squared=False)
print(f'Root Mean Squared Error: {rmse}')

# Predictions and Testing
# Load 3rd year data for testing
test_year = '2000'  # Adjust to your desired year
test_data = pd.read_excel('path_to_your_excel_file.xlsx', sheet_name=test_year)
test_data['Date'] = pd.to_datetime(test_data['Date'])
test_data['Days'] = (test_data['Date'] - combined_data['Date'].min()).dt.days
test_data['Month'] = test_data['Date'].dt.month

# Make predictions on the test data
test_predictions = model.predict(test_data[features])

# Compare predictions with actual results
test_data['PredictedLastThreeDigits'] = test_predictions
comparison = pd.DataFrame({
    'Date': test_data['Date'],
    'ActualLastThreeDigits': test_data['LastThreeDigits'],
    'PredictedLastThreeDigits': test_predictions
})

# Assuming you have verified if the predictions are correct for the test data
if predictions_are_correct:
    # Update the training data with the correct predictions
    combined_data = combined_data.append(test_data, ignore_index=True)

    # Re-preprocess the updated data
    combined_data['Date'] = pd.to_datetime(combined_data['Date'])
    combined_data['Days'] = (combined_data['Date'] - combined_data['Date'].min()).dt.days
    combined_data['Month'] = combined_data['Date'].dt.month

    # Update features and target
    X = combined_data[features]
    y = combined_data[target]

    # Retrain the model with updated data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate the updated model
    val_predictions = model.predict(X_val)
    rmse = mean_squared_error(y_val, val_predictions, squared=False)
    print(f'Updated Root Mean Squared Error: {rmse}')
