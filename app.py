# many of these codes are copied from my jupyter notebook file
# because the questions are very similar from part 1

from flask import Flask, jsonify
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///resource/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station


app = Flask(__name__)


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (
        f'Welcome to the Hawaii Weather API!<br/>'
        f'Available Routes:<br/>'
        f'<br/>'
        f'Returns precipitation data:<br/>'
        f'/api/v1.0/precipitation<br/>'
        f'<br/>'
        f'Returns stations data:<br/>'
        f'/api/v1.0/stations<br/>'
        f'<br/>'
        f'returns temperature observed for previous year data:<br/>'
        f'/api/v1.0/tobs<br/>'
        f'<br/>'
        f'Returns various temperature data for a given [START] date, or [START] to [END] range:<br/>'
        f'Note: [START] and [END] are dates in yyyy-mm-dd format.<br/>'
        f'Example: /api/v1.0/2012-05-28<br/>'
        f'/api/v1.0/[START]<br/>'
        f'/api/v1.0/[START]/[END]<br/>'
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    return_json = []
    sel = [Measurement.date, func.avg(Measurement.prcp)]
    prcpdata = session.query(*sel).group_by(Measurement.date).all()
    session.close()

    for date, prcp in prcpdata:
        dictionary = {}
        dictionary["date"] = date
        dictionary["prcp"] = prcp
        return_json.append(dictionary)

    return jsonify(return_json)


@app.route("/api/v1.0/stations")
def stations():

    return_json = []
    sel = [Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    stationdata = session.query(*sel).all()
    session.close()

    for station, name, lat, long, elev in stationdata:
        dictionary = {}
        dictionary["station"] = station
        dictionary["name"] = name
        dictionary["latitude"] = lat
        dictionary["longitute"] = long
        dictionary["elevation"] = elev
        return_json.append(dictionary)

    return jsonify(return_json)


@app.route("/api/v1.0/tobs")
def tobs():

    return_json = []
    last12month = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    lastyear = dt.datetime.strptime(last12month, "%Y-%m-%d") - dt.timedelta(days=365)
    activestation = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    sel = [Measurement.date, Measurement.tobs]
    tempdata = session.query(*sel).filter(Measurement.date >= lastyear).filter(Measurement.station == activestation[0][0]).all()
    session.close()

    for date, tobs in tempdata:
        dictionary = {}
        dictionary["date"] = date
        dictionary["tobs"] = tobs
        return_json.append(dictionary)
    
    return jsonify(return_json)


@app.route("/api/v1.0/<start>")
def tempstart(start):

    return_json = []
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    tempdatastart = session.query(*sel).filter(Measurement.date >= start).group_by(Measurement.date).all()
    session.close()

    for date, tmin, tmax, tavg in tempdatastart:
        dictionary = {}
        dictionary["date"] = date
        dictionary["min_temp"] = tmin
        dictionary["max_temp"] = tmax
        dictionary["avg_temp"] = tavg
        return_json.append(dictionary)

    return jsonify(return_json)


@app.route("/api/v1.0/<start>/<end>")
def tempstartend(start, end):
    
    return_json = []
    sel = [Measurement.date, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
    tempdatastartend = session.query(*sel).filter(Measurement.date >= start).filter(Measurement.date <= end).\
        group_by(Measurement.date).all()
    session.close()

    for date, tmin, tmax, tavg in tempdatastartend:
        dictionary = {}
        dictionary["date"] = date
        dictionary["min_temp"] = tmin
        dictionary["max_temp"] = tmax
        dictionary["avg_temp"] = tavg
        return_json.append(dictionary)

    return jsonify(return_json)


if __name__ == "__main__":
    app.run(debug=True)
