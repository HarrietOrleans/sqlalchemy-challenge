# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
from datetime import datetime, timedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
print(Base.classes.keys())

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB

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
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    with Session(engine) as session:
        end_date = session.query(func.max(Measurement.date)).one()[0]
        end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')
        one_year_ago = end_date - dt.timedelta(days=365)

        precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

        precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    with Session(engine) as session:
        results = session.query(Station.station).all()
        stations_list = [result[0] for result in results]

    return jsonify(stations_list)


@app.route("/api/v1.0/tobs")
def tobs():
    with Session(engine) as session:
        last_date = session.query(func.max(Measurement.date)).one()[0]
        last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
        one_year_ago = last_date - dt.timedelta(days=365)

        most_active_station = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

        tobs_data = session.query(Measurement.tobs).filter(Measurement.station == most_active_station).filter(Measurement.date >= one_year_ago).all()

        tobs_list = [tob[0] for tob in tobs_data]

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start=None, end=None):
    with Session(engine) as session:
        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        if end:
            end_date = dt.datetime.strptime(end, '%Y-%m-%d')
        else:
            end_date = session.query(func.max(Measurement.date)).one()[0]
            end_date = dt.datetime.strptime(end_date, '%Y-%m-%d')

        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

        temp_stats = {
            "TMIN": results[0][0],
            "TAVG": results[0][1],
            "TMAX": results[0][2]
        }

    return jsonify(temp_stats)


if __name__ == '__main__':
    app.run(debug=True)


