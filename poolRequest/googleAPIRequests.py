import requests
import logging
#from sserver import apiKey
apiKey ='AIzaSyAoUGzwRMXGeO9X8_QApT6cB85FOV2ec9Y'


def getDirections(origin, desitnation ,modeOfTransport, waypoints):
    logging.info("Getting Directions from "+str(origin)+" to "+str(desitnation))
    waypointsString=processWaypoints(waypoints)

    #check if locations are passed in tuple format
    if tuple == type(origin):
        origin=tupleLatLongToString(origin)
    if tuple == type(desitnation):
        desitnation=tupleLatLongToString(desitnation)


    requestString=\
        ("https://maps.googleapis.com/maps/api/directions/json?origin={}&destination={}&mode={}{}&key={}"
            .format(origin, desitnation,modeOfTransport,waypointsString,apiKey))
    logging.info("Request string:"+requestString)
    r = requests.get(requestString).json()
    logging.info("directions are:")
    logging.info(r)
    return r

def getPlaces(latlong,radius):
    logging.info("Get Places around: "+str(latlong)+" in radius "+str(radius))
    latLongString=str(latlong).strip("(").strip(")")
    requestString=("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={}&radius=500&key={}".format(latLongString,apiKey))
    r = requests.get(requestString).json()
    #lat=r['results'][0]['geometry']['location']['lat']
    #lng=r['results'][0]['geometry']['location']['lng']
    #name=r['results'][0]['name']
    logging.info("Places Retrieved")

    return r

def getLatLong(place_name):
    logging.info("Get lat and long")
    #https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
    try:
        requestString=("https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}".format(place_name,apiKey))
        lat_long = requests.get(requestString).json()
        lat=lat_long['results'][0]['geometry']['location']['lat']
        lng=lat_long['results'][0]['geometry']['location']['lng']
        logging.info("Got "+str(lat)+","+str(lng))
        return float(lat),float(lng)
    except Exception:
        latLng=place_name.split(",");
        lat=latLng[0].replace("(", "")
        lng=latLng[1].replace(")", "")
        return float(lat), float(lng)

def processWaypoints(waypoints):
    logging.info("processing waypoints: "+str(waypoints))
    waypointsString=""
    for waypoint in waypoints:
        waypointsString+="|"+str(waypoint).strip("(").strip(")")
        logging.info("Waypoint "+str(waypoint)+" Added to waypointsString")
    logging.info("Waypoints processed "+waypointsString)
    if(waypointsString==""):
        logging.info("No waypoints to process")
        return ""
    return "&waypoints=optimize:true|"+waypointsString

def tupleLatLongToString(lltuple):
    logging.info("convering tuple to string: "+str(lltuple))
    lat, lng =lltuple
    location= "{},{}".format(lat, lng)
    return location