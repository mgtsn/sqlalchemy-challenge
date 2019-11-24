import numpy as np
import pandas as pd

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import datetime as dt
from dateutil.parser import parse

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
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
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"

    )


@app.route("/api/v1.0/precipitation")
def prcp():
    
    session = Session(engine)
    
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    latest = [result[0] for result in results[:1]][0]
    latest = dt.datetime.strptime(latest, '%Y-%m-%d')

    year_ago = latest - dt.timedelta(365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).order_by(Measurement.date.desc()).all()

    session.close()
    
    output = {}
    for r in results:
        output[r[0]] = r[1]
    
    return jsonify(output)


@app.route("/api/v1.0/stations")
def station():
    
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    l = list(np.ravel(results))
    return jsonify(l)

@app.route("/api/v1.0/tobs")
def tobs():
    
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date.desc()).all()
    latest = [result[0] for result in results[:1]][0]
    latest = dt.datetime.strptime(latest, '%Y-%m-%d')

    year_ago = latest - dt.timedelta(365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > year_ago).order_by(Measurement.date.asc()).all()

    session.close()
    l = list(np.ravel(results))
    return jsonify(l)
 
    
@app.route("/api/v1.0/<start>")
def date_start(start):
    
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()
    l = list(np.ravel(results))
    return jsonify(l)
    

@app.route("/api/v1.0/<start>/<end>")
def date_range(start, end):
    
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    
    l = list(np.ravel(results))
    return jsonify(l)

if __name__ == '__main__':
    app.run(debug=True)
