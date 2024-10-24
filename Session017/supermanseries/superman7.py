import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer  # Ensure this is imported
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import threading

# Modify this function to choose a more relevant target column
def auto_select_target(df):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    if numeric_columns.empty:
        raise ValueError("No numeric columns found in the DataFrame.")

    # Choose a different target column if 'Record ID' is not relevant
    potential_target_columns = numeric_columns[numeric_columns != "Record ID"]
    target_column_name = potential_target_columns[0] if not potential_target_columns.empty else numeric_columns[0]

    print(f"Automatically selected numeric target column for regression: {target_column_name}")
    return target_column_name


# Function to preprocess data
def preprocess_data(df, target_column):
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Convert columns to numeric, forcing errors to NaN
    X = X.apply(pd.to_numeric, errors='coerce')

    # Fill missing values
    X = X.fillna(X.mean())
    y = y.fillna(y.mean())

    # Remove any remaining non-numeric columns
    X = X.select_dtypes(include=[np.number])

    return X, y


# Function to plot 2D scatter plots
def plot_2d(df, target_column):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    for col in numeric_columns:
        if col != target_column:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(data=df, x=col, y=target_column)
            plt.title(f"2D Scatter Plot: {col} vs {target_column}")
            plt.xlabel(col)
            plt.ylabel(target_column)
            plt.grid()
            plt.show()


# Function to plot 3D scatter plots
def plot_3d(df, target_column):
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    if len(numeric_columns) >= 3:
        for i in range(len(numeric_columns) - 2):
            for j in range(i + 1, len(numeric_columns) - 1):
                x_col = numeric_columns[i]
                y_col = numeric_columns[j]
                z_col = target_column

                fig = plt.figure(figsize=(10, 8))
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(df[x_col], df[y_col], df[z_col], alpha=0.7)
                ax.set_title(f"3D Scatter Plot: {x_col} vs {y_col} vs {z_col}")
                ax.set_xlabel(x_col)
                ax.set_ylabel(y_col)
                ax.set_zlabel(z_col)
                plt.show()


# Function to analyze data and train model
def analyze_data(df):
    # Summarize dataset
    print("Dataset summary:")
    print(df.describe())
    print("\nData Types:")
    print(df.dtypes)

    # Automatically select the target column
    target_column = auto_select_target(df)
    X, y = preprocess_data(df, target_column)

    # Drop columns with all NaN values
    X = X.dropna(axis=1, how='all')

    # Separate numerical and categorical columns
    numerical_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()

    print("Numerical columns:", numerical_cols)
    print("Categorical columns:", categorical_cols)

    # Create transformers based on the availability of categorical columns
    transformers = [('num', SimpleImputer(strategy='mean'), numerical_cols)]

    # Only add the categorical transformer if there are categorical columns
    if categorical_cols:
        transformers.append(('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols))

    # Create a ColumnTransformer for preprocessing
    preprocessor = ColumnTransformer(transformers=transformers)

    # Create a pipeline with preprocessing and the model
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('model', LinearRegression())])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit the pipeline on the training data
    pipeline.fit(X_train, y_train)

    # Transform the training data to get the final feature names
    X_train_transformed = pipeline.named_steps['preprocessor'].transform(X_train)

    # Retrieve numerical column names
    num_feature_names = numerical_cols

    # Retrieve categorical column names if available
    if categorical_cols:
        cat_feature_names = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(
            categorical_cols)
        feature_names = num_feature_names + list(cat_feature_names)
    else:
        feature_names = num_feature_names

    # Calculate feature importance from the model
    feature_importance = pd.DataFrame(pipeline.named_steps['model'].coef_, index=feature_names, columns=["Coefficient"])
    print("Feature importance:\n", feature_importance)

    # Make predictions on the test data
    y_pred = pipeline.predict(X_test)

    # Calculate performance metrics
    mse = mean_squared_error(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    # Print model performance metrics
    print("\nModel Performance Metrics:")
    print(f"Mean Squared Error (MSE): {mse}")
    print(f"Mean Absolute Error (MAE): {mae}")
    print(f"R² Score: {r2}")

    # Plot 2D and 3D graphs (assuming these functions are defined elsewhere)
    # plot_2d(df, target_column)
    # plot_3d(df, target_column)
    # Start plotting in separate threads
    plot_2d_thread = threading.Thread(target=plot_2d, args=(df, target_column))
    plot_3d_thread = threading.Thread(target=plot_3d, args=(df, target_column))

    plot_2d_thread.start()
    plot_3d_thread.start()

    # Wait for both threads to complete
    plot_2d_thread.join()
    plot_3d_thread.join()
    # Display model details
    print("\nModel Details:")
    print(pipeline.named_steps['model'])


# Main function to load data and run analysis
def main(file_path):
    df = pd.read_csv(file_path)  # Load your dataset here
    print(f"Dataset loaded with {df.shape[0]} rows and {df.shape[1]} columns.")

    analyze_data(df)


if __name__ == "__main__":
    file_path = r"C:\Users\HimakarRaju\Desktop\PreSkilling\Python\Data_Science_And_Visualization\Session023\winequality-red.csv"  # Update with your file path
    main(file_path)
