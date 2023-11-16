# Import necessary libraries
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create engine and reflect the database
engine = create_engine("sqlite:////Users/davidshetler/Desktop/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session
session = Session(engine)

# Create an app instance
app = Flask(__name__)

# Define routes
@app.route("/")
def home():
    """Homepage and list of available routes."""
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date (replace start_date with a date in 'YYYY-MM-DD' format)<br/>"
        f"/api/v1.0/start_date/end_date (replace start_date and end_date with dates in 'YYYY-MM-DD' format)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data as JSON."""
    # Calculate the date one year ago from the most recent date
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    # Query precipitation data for the last 12 months
    precipitation_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    stations = session.query(Station.station).all()
    station_list = [station[0] for station in stations]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year (most active station)."""
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    temperature_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()

    return jsonify(temperature_data)

@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    """Return JSON list of TMIN, TAVG, and TMAX for dates greater than or equal to the start date."""
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    return jsonify({"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][1], "TMAX": temperature_stats[0][2]})

@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    """Return JSON list of TMIN, TAVG, and TMAX for dates between the start and end date, inclusive."""
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()

    return jsonify({"TMIN": temperature_stats[0][0], "TAVG": temperature_stats[0][1], "TMAX": temperature_stats[0][2]})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
