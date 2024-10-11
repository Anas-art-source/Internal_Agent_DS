import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import ChatMessage
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import matplotlib.dates as mdates

def create_prediction_dataframe(start_date, end_date):
    # Generate a range of dates from start_date to end_date
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Create an empty DataFrame with the date range as index
    empty_df = pd.DataFrame({'Date': date_range})
    
    return empty_df

def forecasting_model_inference_api(sales_dataframe, start_date, end_date):
    feature_map = {}
    if 'sales' not in sales_dataframe.columns:
        raise ValueError(f"No 'sales' column in sales dataframe. It contain columns: {sales_dataframe.columns}. You should rename column to 'sales'. Remember you should only submit sales dataframe with two columns only: 'sales' and 'date'")
    if 'date' not in sales_dataframe.columns:
        raise ValueError(f"No 'date' column in sales dataframe. It contain columns: {sales_dataframe.columns}. You should rename column to 'date'. Remember you should only submit sales dataframe with two columns only: 'sales' and 'date'")
    
    pandas_dataframe = sales_dataframe.copy()
    df = pandas_dataframe.copy()
    categorical_features = list(df.drop(['date', 'sales'], axis=1).columns)
    if len(categorical_features) > 0:
        df = df.drop(categorical_features, axis=1)
    prediction = {}
    print(sales_dataframe.columns, "here in forecasting_model_inference_api")
    df_prediction = sales_dataframe[['date', 'sales']]
    result = fit_predict(df_prediction, start_date=start_date, end_date=end_date)
    return result

def fit_predict(df, start_date, end_date):
    metrics = {}
    df['Date'] = pd.to_datetime(df['date'])
    df.sort_values('Date', inplace=True)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday
    numerical_features = ['Year', 'Month', 'Day', 'Weekday']
    numerical_transformer = StandardScaler()

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_features),
        ])
    X = df[numerical_features]

    xgb_regressor = XGBRegressor()
    pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                               ('regressor', xgb_regressor)])

    y = df['sales']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    metrics['mse'] = mean_squared_error(y_test, predictions)

    date_dataframe = create_prediction_dataframe(start_date=start_date, end_date=end_date)
    results, plot = agent_inference(pipeline, date_dataframe)
    metrics['total_forecast'] = np.sum(results)
    return metrics

def agent_inference(pipeline, date_dataframe):
    df = date_dataframe.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Weekday'] = df['Date'].dt.weekday
    X = df.copy()
    predictions = pipeline.predict(X)
    plt.style.use('dark_background')
    plt.plot(df['Date'], predictions, color='cyan')  # Cyan stands out on a dark background
    plt.xticks(rotation=45, ha='right')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    plt.grid(color='gray', linestyle=':', linewidth=0.5)
    plt.tick_params(colors='white', which='both')  # Change the colors of the tick marks to white
    plt.tight_layout()
    plt.show()
    return predictions, plt

# Example usage
# from pants_data_api import pants_data_api
# data = pants_data_api(is_store_level=True)
# print(forecasting_model_inference_api(data, start_date='2024-01-01', end_date='2024-01-31'))
