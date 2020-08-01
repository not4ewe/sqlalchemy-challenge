import sqlalchemy

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
        f"<h2>Welcome to the Hawaii Climate API</h2><br/>"
        f"<h4>Available Routes:</h4>"
        f"1. /api/v1.0/precipitation<br/>"
        f"2. /api/v1.0/stations<br/>"
        f"3. /api/v1.0/tobs<br/>"
        f"4. /api/v1.0/yyyy-mm-dd/<br/>"
        f"5. /api/v1.0/yyyy-mm-dd/yyyy-mm-dd/"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return precipitation data"""
    # Query all measurements
    results=session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    # Convert query results to a dictionary
    daily_precip = {}
    for date,precipitation in results:
        daily_precip[date] = precipitation
        
    return jsonify(daily_precip)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.station, Station.name).all()

    session.close()

    # Return a JSON list of stations from the dataset.
    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of tobs"""
    # Query the dates and temperature observations of the most active station for the last year of data.

    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()
    (most_active_station_id, ) = most_active_station

    active_tobs = session.query(Measurement.date).\
    order_by(Measurement.date.desc()).\
    filter(Measurement.station == most_active_station_id).first()

    (latest_date,) = active_tobs
    latest_date = dt.datetime.strptime(latest_date, '%Y-%m-%d')
    latest_date = latest_date.date()
    date_year_ago = latest_date - relativedelta(years=1)

    last_year_data = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == most_active_station_id).\
    filter(Measurement.date >= date_year_ago).all()

    session.close()

    #Return a JSON list of temperature observations (TOBS) for the previous year.
    temperatures = []
    for date, tobs in last_year_data:
            temp_dict = {}
            temp_dict["date"]= date
            temp_dict["tobs"]= tobs
            temperatures.append(temp_dict)

    return jsonify(temperatures)


@app.route("/api/v1.0/<start_date>/")
def temp_stats(start_date):

    #Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start range"""
    # Query temperatures by start date
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).first()
    
    #create dictionary from result
    temps_dictionary1 = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dictionary1)


@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_range(start_date, end_date):
    
    #Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    # Query temperature by start-end range.
    temps = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date, Measurement.date <= end_date).first()
    
    #create dictionary from result
    temps_dictionary2 = {"TMIN": temps[0], "TMAX": temps[1], "TAVG": temps[2]}
    return jsonify(temps_dictionary2)

if __name__ == '__main__':
    app.run(debug=True)
