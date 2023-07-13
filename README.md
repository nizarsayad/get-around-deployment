![GetAround logo](Getaround_(Europe).png)

# Project 05: GetAround Deployment

**Certificate - Machine Learning Engineer**

**Bloc 5 - Deployment**

## Introduction

[**GetAround dashboard**](https://getaround-dashboard-ns-5cd53cf17cd7.herokuapp.com/)

[**GetAround API documentation**](http://ec2-35-180-36-210.eu-west-3.compute.amazonaws.com/docs)

GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.

This project is part of the professional certification Machine Learning Engineer (Concepteur Développeur en Science des données) and represents bloc 5 of the certification titled: "Deployment".

### Context

When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout.

Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time.

In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental.

It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off.

We still needs to decide:

- threshold: how long should the minimum delay be?
- scope: should we enable the feature for all cars?, only Connect cars?

## Project Structure

The project consists of several components:

- `getaround-analysis`: This is the main directory
    - `00-src`: Contains the data files for the project.
    
    - `01-streamlit`: This directory contains all the elements necessary to run the web app dashboard using the streamlit library.
        - `.streamlit`: This is the configuration folder for the streamlit app.
        - `app.py`: python script to run the app
        - `Dockerfile`: Dockerfile to build the image
        - `getaround_analysis.ipynb`: notebook of the data analysis done
        - `notes.md`: notes related to the analysis
        - `get_around_delay_analysis.xlsx`: data file for the analysis
        - `get_around_pricing_project.csv`: data file for model training
        - `requirements.txt`: libraries to be installed when building the image
        - `run.sh`: bash command to run the Docker container locally
    
    - `02-mlflow`: This directory contains all the elements necessary to run our mlflow tracking server
        - `Dockerfile`: Dockerfile to build the image
        - `requirements.txt`: libraries to be installed when building the image
        - `run.sh`: bash command to run the Docker container locally
    
    - `03-machine-learning`: This directory contains all the elements necessary to train our regressor model.
        - `get_around_pricing_project.csv`: data file for model training
        - `notes.md`: notes related to the initial data exploration
        - `pricing_project.ipynb`: notebook of the model training

    - `04-api`: This directory contains all the elements necessary to run our inference API
        - `app.py`: python script to run the app
        - `Dockerfile`: Dockerfile to build the image
        - `requirements.txt`: libraries to be installed when building the image
        - `run.sh`: bash command to run the Docker container locally
        - `build.sh`: bash command to build the Docker image

- `README.md`: This file provides an overview of the project.

## Additional information

- Some applications require environment variables. 
    - There are two ways to define and pass these variables:
        - `secrets.sh`: 
            ```bash
            export PORT=
            export AWS_ACCESS_KEY_ID=
            export AWS_SECRET_ACCESS_KEY=
            export BACKEND_STORE_URI=
            export ARTIFACT_ROOT=
            export MLFLOW_TRACKING_URI=
            ```
        - `.env`:
        ```env
        PORT=
        AWS_ACCESS_KEY_ID=
        AWS_SECRET_ACCESS_KEY=
        BACKEND_STORE_URI=
        ARTIFACT_ROOT=
        MLFLOW_TRACKING_URI=
        ```
    - These files should be used depending on the use case:
        - if we want to pass env variables to a notebook, then we must use .env file since ```source secrets.sh``` only works if we're running a script or a comand from the terminal (e.g: running docker images or a python script)
- The API is running on AWS EC2 instance
- The dashboard as well as the mlflow tracking server are hosted on [Heroku](https://dashboard.heroku.com/): 