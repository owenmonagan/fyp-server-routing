from googleAPIRequests import getLatLong, getDirections
import random
#from jsonProcessing import getEtaOfLeg

class poolDirections():

    def __init__(self, leader, members):
        self.leader = leader
        self.members = members
        self.id = random.randint(0, 1000)



class poolMember():
    def __init__(self, name, origin, methodOfTransport):
                self.id= random.randint(0,1000)
                self.name = name
                self.origin = getLatLong(origin)
                self.originString = origin
                self.methodOfTransport = methodOfTransport
                self.meetPoint = None
                self.placesNear = None
                self.eta = None
                self.directionsToMeetPoint = None

    def storePlacesAndSelectMeetPoint(self,places):
        self.setMeetPoint(places[0])
        self.setPlaces(places)

    def setMeetPoint(self,meetPoint):
        self.meetPoint=meetPoint

    def setPlaces(self,places):
        self.placesNear=places

    def setDirections(self):
        self.directionsToMeetPoint = getDirections(self.origin,self.meetPoint.location,self.methodOfTransport,[])
        seconds , mins=self.getEtaOfLeg(self.directionsToMeetPoint['routes'][0]['legs'][0])
        self.eta=seconds

    def getDirections(self):
        return self.directionsToMeetPoint

    def getEtaOfLeg(self,leg):
        seconds=int(leg['duration']['value'])
        minutesString=leg['duration']['text']
        return seconds,minutesString

    def getEta(self, directions):
        etaInSeconds=0
        for leg in directions['routes'][0]['legs']:
            seconds, textMins=self.getEtaOfLeg(leg)
            etaInSeconds+=seconds
        return etaInSeconds

    def __repr__(self):
            return repr((self.name, self.origin, self.methodOfTransport, self.directionsToMeetPoint,self.placesNear,self.meetPoint))




class place():
    def __init__(self,name,location,types):
        self.name=name
        self.location= location
        self.types=types
        self.membersMeetPoint=None
        self.distanceFromPoint=None
        self.distanceLat=None
        self.distanceLng=None

    def setMeetPointInformation(self,membersMeetPoint,distanceFromPoint,distanceLat,distanceLng):
        self.membersMeetPoint=membersMeetPoint
        self.distanceFromPoint=distanceFromPoint
        self.distanceLat=distanceLat
        self.distanceLng=distanceLng



class poolLeader(poolMember):

    def __init__(self, name, origin, destination, methodOfTransport):
            self.id= random.randint(0,1000)
            self.name = name
            self.origin = getLatLong(origin)
            self.originString=origin
            self.destination = getLatLong(destination)
            self.destinationString = destination
            self.methodOfTransport = methodOfTransport
            self.directions=None
            self.wayPoints=None
            self.eta=None
            self.etaToMembers=[]

    def setWayPoints(self, waypoints):
        self.wayPoints = waypoints

    def updateDirections(self):
        self.directions = getDirections(self.origin,self.destination,self.methodOfTransport,self.wayPoints)
        totalseconds=0
        etasOfMember=[]
        for leg in self.directions['routes'][0]['legs']:
            seconds, mins = self.getEtaOfLeg(leg)
            etasOfMember.append(seconds)
            totalseconds += seconds
        self.eta = totalseconds
        self.etaToMembers = etasOfMember



    def getDirections(self):
        return self.directions

    def __repr__(self):
        return repr((self.name, self.origin, self.destination, self.methodOfTransport,self.directions,self.wayPoints))
