import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

###########################################################################################################################
# Database Setup
###########################################################################################################################
# Set 'check_same_thread'to False to avoid errors cause by refreshing browser
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)
###########################################################################################################################


###########################################################################################################################
# Flask Setup
app = Flask(__name__)
###########################################################################################################################


###########################################################################################################################
###########################################################################################################################
# Flask Routes
###########################################################################################################################
###########################################################################################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/<start><br/>"
        f"/api/<start>/<end>"
    )
###########################################################################################################################

###########################################################################################################################
@app.route("/api/precipitation")
def precipitation_route():
    """Return date and precipitation for ALL observations in Measurement data"""

    # Query ALL observations for precipitation
    prcp_list = session.query(Measurement.date,Measurement.prcp).order_by(Measurement.date).all()

    precipitation = []
    for date, prcp in prcp_list:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)
    return jsonify(precipitation)

###########################################################################################################################

###########################################################################################################################
@app.route("/api/stations")
def station_route():
    """Return a list of all stations"""

    # Query all waether stations
    stations_list = session.query(Measurement.station).group_by(Measurement.station).all()
    stations_list = list(np.ravel(stations_list))

    all_stations = []
    for station_i in stations_list:
        all_stations.append(station_i)
    return jsonify(all_stations)
###########################################################################################################################

###########################################################################################################################
@app.route("/api/temperature")
def temperature_route():
    """Return ALL temperature observations for the last year of data"""
   
    # Find final date in the data and set initial date to be 1 year before final date
    final_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    final_date = dt.datetime.strptime(final_date[0], '%Y-%m-%d').date()
    initial_date = final_date + dt.timedelta(-365)

    # Query temprature observations BETWEEN start_date and end_date
    tobs_list = session.query(Measurement.date,Measurement.tobs).\
                order_by(Measurement.date).filter(Measurement.date >= initial_date).all()

    temperature = []
    for date, tobs in tobs_list:
        temperature_dict = {}
        temperature_dict["date"] = date
        temperature_dict["tobs"] = tobs
        temperature.append(temperature_dict)
    return jsonify(temperature)
###########################################################################################################################

###########################################################################################################################
@app.route("/api/<start_date>")
def temperature_start_route(start_date):
    """Return TMIN, TAVE, TMAX for start_date """

    # Query TMIN, TAVE, TMAX for input date
    tobs_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date).all()
    
    temperature = []
    for tmin, tave, tmax in tobs_list:
        temperature_dict = {}
        temperature_dict["TMIN"] = tmin
        temperature_dict["TAVE"] = tave
        temperature_dict["TMAX"] = tmax
        temperature.append(temperature_dict)
    return jsonify(temperature)
###########################################################################################################################

###########################################################################################################################
@app.route("/api/<start_date>/<end_date>")
def temperature_start_end_route(start_date,end_date):
    """Return TMIN, TAVE, TMAX for a range of dates"""

    # Query TMIN, TAVE, TMAX for input date range
    tobs_list = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start_date,Measurement.date <= end_date).all()
    
    temperature = []
    for tmin, tave, tmax in tobs_list:
        temperature_dict = {}
        temperature_dict["TMIN"] = tmin
        temperature_dict["TAVE"] = tave
        temperature_dict["TMAX"] = tmax
        temperature.append(temperature_dict)
    return jsonify(temperature)
###########################################################################################################################

if __name__ == '__main__':
    app.run(debug=True)