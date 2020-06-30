# -*- coding: utf-8 -*-
'''
Created on Jul 29, 2019

@author: Admin
'''
import pandas as pd
from flask import Flask
from flask import render_template
from datetime import date
import json
from shapely.geometry import Point, shape


data_path = './input/'
n_samples = 10000

def get_age_segment(age):
    if age <= 15:
        return '<15'
    elif age <= 25:
        return '16-25'
    elif age <= 35:
        return '26-34'
    elif age <= 45:
        return '36-45'
    elif age <= 55:
        return '46-55'
    else:
        return '56++'

with open(data_path + '/geojson/district.geojson', encoding="utf-8" ) as data_file:
    provinces_json = json.load(data_file)

def get_location(longitude, latitude, provinces_json):
    point = Point(longitude, latitude)
    for record in provinces_json['features']:
        polygon = shape(record['geometry'])
        if polygon.contains(point):
            return record['properties']['Ten_Tinh']
    return 'other'

gend = {'True': 'Male', 'False': 'Female'}
sod={1:"PTB",2:"ETB"}

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    data = pd.read_csv('m.csv', encoding="ISO-8859-1")
    #data = data.sample(n=n_samples)
    #data["admission"] = pd.to_datetime(data["admission"], format="%d/%m/%Y", errors='coerce')
    data['REGISTRATIONDATE'] = pd.to_datetime(data['REGISTRATIONDATE']).dt.normalize()
    #data["dob"] = pd.to_datetime(data["dob"], format="%d/%m/%Y", errors='coerce')
    #data["age"] = (data["onset"] - data["dob"]).astype('<m8[Y]') 
    data['location'] = data.apply(lambda row: get_location(row['PA_LONG'], row['PA_LAT'], provinces_json), axis=1)
    data.dropna()
    #print(data['GENDER'])
    data.GENDER = data.GENDER.astype(str)
    data['GENDER'] = data['GENDER'].apply(lambda x: gend[x])
    data['age_segment'] = data['AGE'].apply(lambda age: get_age_segment(age))
    data.SITEOFDISEASE = data.SITEOFDISEASE.apply(lambda x: sod[x])
    #print(data.to_json(orient='records'))
    return data.to_json(orient='records')

if __name__ == "__main__":
    app.run(debug='TRUE')
    
    
    