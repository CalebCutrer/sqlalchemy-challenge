# Import the dependencies.
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with = engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
#Session = sessionmaker(bind=engine)
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# All routes:
@app.route("/")
def homepage():
    """List all available routes."""
    return(
        f"Welcome!<br/>"
        f"Avaliable Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Precipitation:
@app.route("/api/v1.0/precipitation")
def precipitation():
    # find most recent date and date for one year prior
    most_recent_date = session.query(func.max(measurement.date))
    one_year_prior = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    # query for date and prcp data
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year_prior).all()
    # convert to dictionary and jsonify
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    return jsonify(precipitation_data)

# Stations:
@app.route("/api/v1.0/stations")
def stations():
    # query the list of all stations
    results = session.query(station.station).all*()
    # return jsonified list of all stations
    station_list = []
    for station, in results:
        station_list.append(station)
    
    return jsonify(station_list)

# Tobs: 
@app.route("/api/v1.0/tobs")
def tobs():
    # find most active station 
    most_active_station = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()
    #grab past year's data for this station
    most_active_last_date = session.query(func.max(measurement.date)).\
        filter(measurement.station == most_active_station)
    one_year_most_active = dt.datetime.strptime(most_active_last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    #query the temp observations for this station
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_year_most_active).all()
    #convert query results to list of dictionaries and jsonify
    tobs_dicts = [{'date': date, 'tobs': tobs} for date, tobs in results]

    return jsonify(tobs_dicts)

# Start and End routes:
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temp(start=None, end=None):
    """Return TMIN, TAVG, TMAX for a given start or start-end range."""
    # Select statement for min, max, avg
    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        # Find TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(measurement.date >= start).all()
    else:
        # Calculate TMIN, TAVG, TMAX for dates between start and end
        results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    # Converting list of tuples into dict
    temperature_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    return jsonify(temperature_data)

if __name__ == "__main__":
    app.run(debug=True)



