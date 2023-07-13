import mlflow 
import uvicorn
import json
import pandas as pd 
from pydantic import BaseModel
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import os

description = """
GetAround pricing API helps you estimate the daily rental price of a car.
The goal of this api is to serve data that help potential owners estimate the value of their assets on our platform
based on the car's characteristics.

## Preview

Where you can: 
* `/preview` a few rows of your dataset
* get `/unique-values` of a given column in your dataset

## Categorical

Where you can: 
* `/groupby` a given column and chose an aggregation metric 
* `/filter-by` one of several categories within your dataset 

## Numerical 

Where you can: 
* Get a subset of your data given a certain `/quantile` 


## Machine-Learning 

Where you can:
* `/predict` the price estimation of a car given its characteristics
* `/batch-predict` where you can upload a file to get predictions for several cars


Check out documentation for more information on each endpoint. 
"""

tags_metadata = [
    {
        "name": "Categorical",
        "description": "Endpoints that deal with categorical data",
    },

    {
        "name": "Numerical",
        "description": "Endpoints that deal with numerical data"
    },

    {
        "name": "Verification",
        "description": "Endpoints that help you verify your mlflow server"
    },

    {
        "name": "Preview",
        "description": "Endpoints that quickly explore dataset"
    },

    {
        "name": "Predictions",
        "description": "Endpoints that uses our Machine Learning model for detecting attrition"
    }
]

app = FastAPI(
    title="👨‍💼 GetAround Pricing API",
    description=description,
    version="0.1",
    contact={
        "name": "Nizar Sayad - ML Engineer",
        "url": "https://github.com/nizarsayad",
    },
    openapi_tags=tags_metadata
)

model_name = "getaround_xgbr"
client = mlflow.MlflowClient()
model_version = client.get_registered_model(name=model_name).latest_versions[0].version
model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{model_version}")

class GroupBy(BaseModel):
    column: str
    by_method: Literal["mean", "median", "max", "min", "sum", "count"] = "mean"

class FilterBy(BaseModel):
    column: str
    by_category: List[str]= None

class PredictionFeatures(BaseModel):
    model_key: str
    mileage: Union[int, float]
    engine_power: Union[int, float]
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool

df = pd.read_csv("get_around_pricing_project.csv")
df.drop(columns=["Unnamed: 0", "rental_price_per_day"], inplace=True)    

@app.get("/verification", tags=["Verification"])
async def verif_mlflow():
    """
    Verify that your mlflow server is running correctly
    """
    track_uri_env = os.environ.get("MLFLOW_TRACKING_URI")
    mlflow_tracking_uri = mlflow.get_tracking_uri()
    mlflow_artifact_uri = mlflow.get_artifact_uri()

    return {"mlflow_tracking_uri": mlflow_tracking_uri, "mlflow_artifact_uri": mlflow_artifact_uri, "track_uri_env": track_uri_env}

@app.get("/preview", tags=["Preview"])
async def random_cars(rows: int=10):
    """
    Get a sample of your whole dataset. 
    You can specify how many rows you want by specifying a value for `rows`, default is `10`
    """
    sample = df.sample(rows)
    return sample.to_json()


@app.get("/unique-values", tags=["Preview"])
async def unique_values(column: str):
    """
    Get unique values from a given column 
    """
    df = pd.Series(df[column].unique())

    return df.to_json()

@app.get("/quantile", tags=["Numerical"])
async def quantile(column: str , percent: float = 0.1, top: bool = True):
    """
    Get a values of the rental prices dataset according above or below a given quantile. 
    *i.e* with this dataset, you can have the top 10% values of the dataset given a certain column
    
    You can choose whether you want the top quantile or the bottom quantile by specify `top=True` or `top=False`. Default value is `top=True`
    Accepted values for percentage is a float between `0.01` and `0.99`, default is `0.1`
    """


    if percent > 0.99 or percent <0.01:
        msg = "percentage value is not accepted"
        return msg
    else:
        if top:
            df = df[ df[column] > df[column].quantile(1-percent)]
        else:
            df = df[ df[column] < df[column].quantile(percent)]

        return df.to_json()

@app.post("/groupby", tags=["Categorical"])
async def group_by(groupBy: GroupBy):
    """
    Get data grouped by a given column. Accepted columns are:

    * `['model_key', 'fuel', 'paint_color', 'car_type', 'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires']`

    You can use different method to group by category which are:

    * `mean`
    * `median`
    * `min`
    * `max`
    * `sum`
    * `count`
    """
    

    method = groupBy.by_method

    if method=="mean":
        df = df.groupby(groupBy.column).mean()
    if method=="median":
        df = df.groupby(groupBy.column).median()
    if method=="min":
        df = df.groupby(groupBy.column).min()
    if method=="max":
        df = df.groupby(groupBy.column).max()
    if method=="sum":
        df = df.groupby(groupBy.column).sum()
    if method=="count":
        df = df.groupby(groupBy.column).count()

    return df.to_json()

@app.post("/filter-by", tags=["Categorical"])
async def filter_by(filterBy: FilterBy):
    """
    Filter by one or more categories in a given column. Columns possible values are:

    * `['model_key', 'fuel', 'paint_color', 'car_type', 'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires']`

    Check values within dataset to know what kind of `categories` you can filter by. You can use `/unique-values` path to check them out.
    `categories` must be `list` format.
    """


    if filterBy.by_category != None:
        df = df[df[filterBy.column].isin(filterBy.by_category)]
        return df.to_json()
    else:
        msg = "Please chose a column to filter by"
        return msg


@app.post("/predict", tags=["Machine-Learning"])
async def predict(predictionFeatures: PredictionFeatures):
    """
    Prediction for one observation. Endpoint will return a dictionnary like this:

    ```
    {'prediction': PREDICTION_VALUE[0,1]}
    ```

    You need to give this endpoint all columns values as dictionnary, or form data.
    """
    # Read data 
    df = pd.DataFrame(dict(predictionFeatures), index=[0])

    prediction = model.predict(df)

    # Format response
    response = {"prediction": prediction.tolist()[0]}
    return response


@app.post("/batch-predict", tags=["Machine-Learning"])
async def batch_predict(file: UploadFile = File(...)):
    """
    Make prediction on a batch of observation. This endpoint accepts only **csv files** containing 
    all the trained columns WITHOUT the target variable. 
    """
    # Read file 
    df = pd.read_csv(file.file)

    predictions = model.predict(df)

    return predictions.tolist()

#if __name__=="__main__":
#    uvicorn.run(app, host="0.0.0.0", port=4000, debug=True, reload=True)