# Import the dependencies.
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    most_recent_date = session.query(func.date(func.max(Measurement.date))).scalar()

    twelve_months_ago = session.query(func.date(func.max(Measurement.date), '-365     days')).scalar()

    prcp_scores = session.query(Measurement.date, Measurement.prcp).filter(func.date(Measurement.date) >= twelve_months_ago)
    
    session.close()
    
    prcp_data = {}
    for date, prcp in prcp_scores:
        prcp_data[date] = prcp
    
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    
    stations = session.query(Measurement.station).distinct().all()
    station_names = []
    
    session.close()
    
    station_names = [station[0] for station in stations]
    
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs(): 
    
    latest_date = session.query(func.max(Measurement.date)).filter(Measurement.station == "USC00519281").scalar()
    twelve_months_ago = session.query(func.date(latest_date, '-12 months')).scalar()

    temp_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= twelve_months_ago).filter(Measurement.date <= latest_date).\
    filter(Measurement.station == 'USC00519281').all()
    
    session.close()
    
    temp_list = [{"date": date, "tobs": tobs} for date, tobs in temp_data]

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def get_temp(start):

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    
    session.close()
    
    temp_stats_dict = {
        "start_date": start,
        "temperature_stats": {
            "min_temp": temp_stats[0][0],
            "max_temp": temp_stats[0][1],
            "avg_temp": temp_stats[0][2]
        }
    }

    return jsonify(temp_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def get_temp_range(start, end):

    temp_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    
    temp_stats_dict = {
        "start_date": start,
        "end_date": end,
        "temperature_stats": {
            "min_temp": temp_stats[0][0],
            "max_temp": temp_stats[0][1],
            "avg_temp": temp_stats[0][2]
        }
    }
    
    return jsonify(temp_stats_dict)


if __name__ == '__main__':
    app.run(debug=True)
