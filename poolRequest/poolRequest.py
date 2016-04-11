import logging
from jsonProcessing import getEtaOfLeg, getEta, getLeg, convertValidPlacesTypesToObjectArray
from googleAPIRequests import getDirections, getPlaces
from sortMembers import getPoolMembersMeetLocations, sortPoolMembersPositionInArrayByRoute
from travelRadiusMethods import calculateLastPointInRadiusIndex, calculateOrderedListOfNearestPlaces, \
    getTravelRadius, findFirstOverLappingPointForMember,findFirstOverLappingPointForMember2
import dataObjects
import traceback

nameIndex=0
locationIndex=1
methodIndex=2

def createResponseMessage(poolLeader,poolMembers):
    logging.info("Creating Response Message")
    responseString=("ResponseMessage\n")
    leaderString="PoolLeader:"
    leaderString+=poolLeader.name+";"
    leaderString+=str(poolLeader.origin)+";"
    leaderString+=str(poolLeader.destination)+";"
    leaderString+=str(poolLeader.eta)+";"
    leaderString+=poolLeader.getDirections()['routes'][0]['overview_polyline']['points']+"\n"
    responseString+=leaderString
    for poolMember in poolMembers:
        memberString="PoolMember:"
        memberString+=poolMember.name+";"
        memberString+=str(poolMember.origin)+";"
        memberString+=poolMember.meetPoint.name+"<>"
        memberString+=str(poolMember.meetPoint.location)+"<>"
        memberString+=str(poolMember.meetPoint.types)+";"
        print str(getEta(poolMember.getDirections()))
        memberString+=str(poolMember.eta)+";"
        memberString+=poolMember.getDirections()['routes'][0]['overview_polyline']['points']+"\n"
        responseString+=memberString

    logging.info("response created: "+responseString)
    print(responseString)
    return responseString

def parsePoolRequest(requestString):
    indexOfFirstMember=3
    indexOfLeader=2
    logging.info("parsePoolRequest")
    lines=requestString.split("\n")
    poolDestination= lines[1].split(":")[1]
    #poolLeaderName, poolLeaderLocation, poolLeaderMethod=lines[2].split(":")[1].split(",")
    poolMembers=[]
    poolLeader=None

    #the first value in poolmembers is the poolLeader eg the driver
    for index, poolMember in enumerate(lines):
        logging.info("Handling line: "+str(index))
        if index>=indexOfLeader:
            poolMemberInformation=poolMember.split(":")[1].split(";")
            poolMemberName=poolMemberInformation[0]
            poolMemberLocation=poolMemberInformation[1]
            poolLMemberMethod=poolMemberInformation[2]

            if index>=indexOfFirstMember:
                poolMemberObject=dataObjects.poolMember(poolMemberName,poolMemberLocation,poolLMemberMethod)
                poolMembers.append(poolMemberObject)
                #poolMembers.append([poolMemberName,poolMemberLocation,poolLMemberMethod])
                logging.info("Parsed and stored member:")
                logging.info(poolMembers[index-indexOfFirstMember].__repr__())
            else:
                poolLeader=dataObjects.poolLeader(poolMemberName,poolMemberLocation,poolDestination,poolLMemberMethod)
                #poolLeader.append(poolMemberName)
                #poolLeader.append(poolMemberLocation)
                #poolLeader.append(poolLMemberMethod)
                logging.info("Parsed and stored leader:")
                logging.info(poolLeader.__repr__())


    logging.info("parsePoolRequest returns pool leader: "+str(poolLeader))
    logging.info("parsePoolRequest returns pool memebers: "+str(poolMembers))
    logging.info("parsePoolRequest returns pool destination: "+str(poolDestination))
    return poolLeader, poolMembers, poolDestination


#Parses Request String
#Then then gets the direct directions
#Then gets the directions to each persons location
def handlePoolRequest(requestString):
    logging.info("handlePoolRequest")
    try:
        poolLeader, poolMembers, poolDirections= initializeFirstRoute(requestString)
    except:
        logging.error(traceback.format_exc())
        return "Failed to compute those directions"


    legIndex=0
    totalSecondsFromPreviousLegs=0

    while (legIndex<len(poolMembers)):
        #Get the directions to the poolMember and the directions from the pool member
        leg=getLeg(poolDirections, legIndex)
        nextLeg=getLeg(poolDirections, legIndex+1)
        logging.info("Calculating directions for: "+poolMembers[legIndex].name)
        #Calculate the time it will take for the poolLeader to arrive at the poolMembers current locatioin
        seconds, minutes = getEtaOfLeg(leg)
        totalSecondsFromPreviousLegs += seconds
        #Using the time generate a travel radius
        radius = getTravelRadius(poolMembers[legIndex],legIndex,poolLeader,totalSecondsFromPreviousLegs)
        #get the places within the travel radius
        places = convertValidPlacesTypesToObjectArray(getPlaces(poolMembers[legIndex].origin, radius))
        #assume that the last point in the directions from the user within the radius is on ideal place to meet.
        legPolylinePoints, indexOfLastPointInRadius=calculateLastPointInRadiusIndex(radius,poolMembers[legIndex].origin,nextLeg)
        #with that point find the closest places. With the first value in the array being the closest
        placesNearestToTheFurthestPossibleTravelPoint=calculateOrderedListOfNearestPlaces(places,legPolylinePoints[indexOfLastPointInRadius])
        #save the meetPoint and calculate the directions
        poolMembers[legIndex].storePlacesAndSelectMeetPoint(placesNearestToTheFurthestPossibleTravelPoint)
        poolMembers[legIndex].setDirections()
        #Then recalculate the full trip and the poolmembers directions
        poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
        poolLeader.setWayPoints(poolMembersMeetLocations)
        poolLeader.updateDirections()
        poolDirections=poolLeader.getDirections()
        #If the directions of both the leader and poolmember overlap
        #then find the point at which they first over lap and then find places near it

        firstOverlappingPointIndex,memberPoints=findFirstOverLappingPointForMember\
            (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'],getLeg(poolDirections,legIndex+1))
        if(not firstOverlappingPointIndex==None):
            print poolMembers[legIndex].name+" recalculating based on overlapping"
            print str(memberPoints[firstOverlappingPointIndex])
            print str (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'])
            print str (poolDirections['routes'][0]['overview_polyline']['points'])

            placesNearestToTheOverLappingPoint=calculateOrderedListOfNearestPlaces(places,memberPoints[firstOverlappingPointIndex])
            poolMembers[legIndex].setMeetPoint(placesNearestToTheOverLappingPoint[0])
            poolMembers[legIndex].meetPoint.location=memberPoints[firstOverlappingPointIndex]
            poolMembers[legIndex].setPlaces(placesNearestToTheOverLappingPoint)
            poolMembers[legIndex].setDirections()
        else:
            firstOverlappingPointIndex2,memberPoints2=findFirstOverLappingPointForMember\
            (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'],getLeg(poolDirections,legIndex))
            if(not firstOverlappingPointIndex2==None):
                print poolMembers[legIndex].name+"2 nd recalculating based on overlapping"
                print str(memberPoints2[firstOverlappingPointIndex2])
                print str (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'])
                print str (poolDirections['routes'][0]['overview_polyline']['points'])
                placesNearestToTheOverLappingPoint=calculateOrderedListOfNearestPlaces(places,memberPoints2[firstOverlappingPointIndex2])
                poolMembers[legIndex].setMeetPoint(placesNearestToTheOverLappingPoint[0])
                poolMembers[legIndex].meetPoint.location=memberPoints2[firstOverlappingPointIndex2]
                poolMembers[legIndex].setPlaces(placesNearestToTheOverLappingPoint)
                poolMembers[legIndex].setDirections()



        #Then recalculate the full trip and the poolmembers directions
        poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
        #poolDirections=getDirections(poolLeader.origin,poolLeader.destination ,poolLeader.methodOfTransport,poolMembersMeetLocations)
        poolLeader.setWayPoints(poolMembersMeetLocations)
        poolLeader.updateDirections()
        poolDirections=poolLeader.getDirections()

        firstOverlappingPointIndex,memberPoints=findFirstOverLappingPointForMember2\
            (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'],poolDirections['routes'][0]['overview_polyline']['points'])
        if(not firstOverlappingPointIndex==None):
            print poolMembers[legIndex].name+" recalculating based on overlapping"
            print str(memberPoints[firstOverlappingPointIndex])
            print str (poolMembers[legIndex].getDirections()['routes'][0]['overview_polyline']['points'])
            print str (poolDirections['routes'][0]['overview_polyline']['points'])

            placesNearestToTheOverLappingPoint=calculateOrderedListOfNearestPlaces(places,memberPoints[firstOverlappingPointIndex])
            poolMembers[legIndex].setMeetPoint(placesNearestToTheOverLappingPoint[0])
            poolMembers[legIndex].meetPoint.location=memberPoints[firstOverlappingPointIndex]
            poolMembers[legIndex].setPlaces(placesNearestToTheOverLappingPoint)
            poolMembers[legIndex].setDirections()



        #Then recalculate the full trip and the poolmembers directions
        poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
        #poolDirections=getDirections(poolLeader.origin,poolLeader.destination ,poolLeader.methodOfTransport,poolMembersMeetLocations)
        poolLeader.setWayPoints(poolMembersMeetLocations)
        poolLeader.updateDirections()
        poolDirections=poolLeader.getDirections()


        print poolDirections['routes'][0]['overview_polyline']['points']

        legIndex+=1 #incriment
        #findRealisticPlaceToMeetLeader(placesWithinRadius,etaLeaderToMember,polyine[indexOfLastPointInRadius],poolMembers[index][methodIndex])
        #use eta of leader to get rough draft of how far one could travell

    responseMessage=createResponseMessage(poolLeader,poolMembers)
    return responseMessage


#THIS IS AN MORE EFFICIENT METHOD OF CALCULATING THE FURTHEST POINT TO WHICH THE PERSON CAN TRAVELL IN X AMOUNT OF TIME
#the member should walk the direction towards the second leg end and also the direction of which the car is coming from.
#i can pass the polyline using via so that I have the general route that I should take
#then calculate the directions to the end location hopping to use the poly line
#catch if its not possible and then try to just get the directions without via
#then I can use the places api to find points near there where the user can be picked up

def findRealisticPlaceToMeetLeader(poolMembers,poolMemberIndex,poolLeader,destination,lastPoint,places):
    placeNearestToLastPoint=0
    currentPoolRoute=poolMembers
    currentPoolRoute[poolMemberIndex][locationIndex]=placeNearestToLastPoint
    poolMemberDirections=getDirections(poolMembers[poolMemberIndex][locationIndex],destination,poolMembers[poolMemberIndex][methodIndex],)
    poolDirections=getDirections(poolMembers[poolMemberIndex][locationIndex],placeNearestToLastPoint,poolMembers[poolMemberIndex][methodIndex],)
    #poolMembers[indexOfPoolMember][locationIndex]=placeLocation


def getIdealMeetingPoints():
    pass
    #get the poly point from the next leg which is on the boundary the places radius
    #point=getPolyPointNearestToTheOuterRadius(placesRadius,directions['polyline'])
    #then find the closest place to that point
    #findClosestPlacetoPoint(point,places)
    #get directions to the nearest palce from the users location
    #eta=getdirectionsEta to the nearestplace
    #get directions
    #if the eta is approximatly
    #if eta is > half of leader eta than
    #    difference= eta - halfleaderEta
     #   how off the calculation was=  difference /eta
     #   repeat with how of the calculation was x length/poly line


def initializeFirstRoute(requestString):
    poolLeader, poolMembers, poolDestination=parsePoolRequest(requestString)
    #extract the locations
    poolMembersMeetLocations=getPoolMembersMeetLocations(poolMembers)
    logging.info("Get directions with each poolmembers origin")
    poolLeader.setWayPoints(poolMembersMeetLocations)
    poolLeader.updateDirections()
    print(poolLeader.getDirections())
    poolDirections=poolLeader.getDirections()
    #poolmember position in array corresponds to directions their leg
    poolMembers=sortPoolMembersPositionInArrayByRoute(poolMembers,poolDirections)
    return poolLeader, poolMembers, poolDirections