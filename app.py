from flask import Flask, jsonify
import datetime as dt
import numpy as np
from datetime import datetime, date
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


engine= create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def home():
    print("Home Page")
    return(
        f"Routes: <br/>"
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/stations'> /api/v1.0/stations</a> Returns list of all stations<br/>"
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/precipitation'> /api/v1.0/precipitation</a> Returns list of precipitation data for the most active station<br/>"
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/precipitation/USC00519397'> /api/v1.0/precipitation/station</a> Returns list of precipitation data for specified station<br/>"        
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/tobs'> /api/v1.0/tobs</a> Returns list of dates and temperatures of the most active station<br/>"
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/2017-06-06'> /api/v1.0/start </a> Returns list of the minimum, maximum, and average temperature for a given start date<br/>"        
        f"<a href = 'http://127.0.0.1:5000/api/v1.0/2017-06-06/2017-06-20'> /api/v1.0/start/end </a> Returns list of minimum, maximum, and average temperature for a given start-end date range<br/>"
    )


@app.route("/api/v1.0/stations")
def stations():
    engine = create_engine("sqlite:///Resources/hawaii.sqlite")

    # reflect an existing database into a new model
    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)

    # Save references to each table
    Station = Base.classes.station

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)


@app.route("/api/v1.0/precipitation")
def precipitation():

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

    """Return a list of the last 12 months of precipitation data of the most active station including the date and prcp"""
    # Design a query to retrieve the last 12 months of precipitation data of the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        limit(1).scalar()

    floor_date = datetime.strptime(session.query(Measurement.date).\
        order_by(Measurement.date.desc()).limit(1).scalar()
        ,'%Y-%m-%d')
    ceiling_date = date(floor_date.year -1, floor_date.month, floor_date.day).strftime('%Y-%m-%d')


    # Query precipitation data
    sel = [Measurement.station, Station.name, Measurement.date, Measurement.prcp]
    results = session.query(*sel).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= ceiling_date).\
        all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precipitations = []
    for precipitation in results:
        precipitation_dict = {}
        #precipitation_dict["station"] = precipitation.station
        #precipitation_dict["station_name"] = precipitation.name
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)


@app.route("/api/v1.0/precipitation/<station>")
def precipitation_for_station(station):
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

    """Return a list of the last 12 months of precipitation data of the station requested including the date and prcp"""
    # Design a query to retrieve the last 12 months of precipitation data of the requested station

    floor_date = datetime.strptime(session.query(Measurement.date).\
        order_by(Measurement.date.desc()).limit(1).scalar()
        ,'%Y-%m-%d')
    ceiling_date = date(floor_date.year -1, floor_date.month, floor_date.day).strftime('%Y-%m-%d')

    # Query precipitation data
    sel = [Measurement.station, Station.name, Measurement.date, Measurement.prcp]
    results = session.query(*sel).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.station == station).\
        filter(Measurement.date >= ceiling_date).\
        all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_precipitations = []
    for precipitation in results:
        precipitation_dict = {}
        precipitation_dict["station"] = precipitation.station
        precipitation_dict["station_name"] = precipitation.name
        precipitation_dict["date"] = precipitation.date
        precipitation_dict["prcp"] = precipitation.prcp
        all_precipitations.append(precipitation_dict)

    return jsonify(all_precipitations)



@app.route("/api/v1.0/tobs")
def tobs():

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

    """Return a list of the last 12 months of tobs data of the most active station including the date and tobs"""
    # Design a query to retrieve the last 12 months of tobs data of the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        limit(1).scalar()

    floor_date_for_most_active_station = datetime.strptime(session.query(func.max(Measurement.date)).\
        filter(Measurement.station == most_active_station).scalar()
        ,'%Y-%m-%d')

    ceiling_date_for_most_active_station = date(floor_date_for_most_active_station.year -1
                                                , floor_date_for_most_active_station.month
                                                , floor_date_for_most_active_station.day).strftime('%Y-%m-%d')
    ceiling_date_for_most_active_station


    # Query tobs data
    sel = [Measurement.station, Station.name, Measurement.date, Measurement.tobs]
    results = session.query(*sel).\
        filter(Measurement.station == Station.station).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= ceiling_date_for_most_active_station).\
        all()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_rows = []
    for row in results:
        tobs_dict = {}
        #tobs_dict["station"] = row.station
        #tobs_dict["station_name"] = row.name
        tobs_dict["date"] = row.date
        tobs_dict["tobs"] = row.tobs
        all_rows.append(tobs_dict)

    return jsonify(all_rows)



@app.route("/api/v1.0/<start_date>")
def min_avg_max_start(start_date):

    engine = create_engine("sqlite:///Resources/hawaii.sqlite")

    # reflect an existing database into a new model
    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)

    # Save references to each table
    Measurement = Base.classes.measurement
    #Station = Base.classes.station

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature from a given start date"""
    print(start_date)

    # Query tobs data
    sel = [func.min(Measurement.tobs).label('tmin')
        , func.avg(Measurement.tobs).label('tavg')
        , func.max(Measurement.tobs).label('tmax')]
    results = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        all()
    
    # Create a dictionary from the row data and append to a list of all_passengers
    all_rows = []
    for row in results:
        tobs_dict = {}
        tobs_dict["tmin"] = row.tmin
        tobs_dict["tavg"] = row.tavg
        tobs_dict["tmax"] = row.tmax
        all_rows.append(tobs_dict)

    return jsonify(all_rows)


@app.route("/api/v1.0/<start_date>/<end_date>")
def min_avg_max_start_end(start_date, end_date):

    engine = create_engine("sqlite:///Resources/hawaii.sqlite")

    # reflect an existing database into a new model
    Base = automap_base()
    # reflect the tables
    Base.prepare(engine, reflect=True)

    # Save references to each table
    Measurement = Base.classes.measurement
    #Station = Base.classes.station

    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range"""
    print(start_date, end_date)
    
    # Query tobs data
    sel = [func.min(Measurement.tobs).label('tmin')
        , func.max(Measurement.tobs).label('tmax')
        , func.avg(Measurement.tobs).label('tavg')]
    results = session.query(*sel).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        all()
    
    # Create a dictionary from the row data and append to a list of all_passengers
    all_rows = []
    for row in results:
        tobs_dict = {}
        tobs_dict["tmin"] = row.tmin
        tobs_dict["tmax"] = row.tmax
        tobs_dict["tavg"] = row.tavg
        all_rows.append(tobs_dict)

    return jsonify(all_rows)

if __name__ == '__main__':
    app.run(debug=True)


@app.route("/api/v1.0/precipitation")
def percipitation():
    prcp = session.query(Measurement.date, Measurement.prcp).all()
    all_prcp = []
    for x in prcp:
        x_dict = {}
        x_dict[x.date] = x.prcp
        all_prcp.append(x_dict)
    
    return jsonify(all_prcp)

    

@app.route("/api/v1.0/stations")
def station():
    stations = session.query(Measurement.station).distinct().all()

    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temperature():
    last_date_query = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    last_date = last_date_query.date

    year_ago = (dt.datetime.strptime(last_date,'%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')
    results = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago).all()
    tobs = list(np.ravel(results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_temp(start,end):
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
