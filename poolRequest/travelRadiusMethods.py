import logging
from dataObjects import place
from jsonProcessing import convertPlaceToObject, get_points_from_leg, get_points_from_polyline

def calculateLastPointInRadiusIndex(radius,location,legHeadingToNextDestination):
    logging.info("Calculate Last Point In radius")
    lastPointIndex=0
    polyline=get_points_from_leg(legHeadingToNextDestination)
    for index, point in enumerate(polyline):
        if isPointInRadius(point, location, radius):
            lastPointIndex=index
    logging.info("Point at index "+str(index)+" is the last one in the radius")
    return polyline, lastPointIndex


def isPointInRadius(point, location, radius):
   # logging.info("Point: "+str(point)+" In Radius: "+str(radius)+" of user location: "+str(location))
    differenceInLatitude=abs(point[0]-location[0])
    differenceInLongitude=abs(point[1]-location[1])
    pointIsInRadius= (differenceInLatitude<radius) and (differenceInLongitude<radius)
    #logging.info("Point: "+str(point)+"is in radius is "+str(pointIsInRadius))
    return pointIsInRadius

def calculateOrderedListOfNearestPlaces(places,point):
    logging.info("OrderingPlacesByNearestToPoint: "+str(point))
    sortedPlaces=[]
    for placeIndex, place in enumerate(places):
        placeObj=place
        differenceLat=placeObj.location[0]-point[0]
        differenceLng=placeObj.location[1]-point[1]
        distanceAway=abs(differenceLat)+abs(differenceLng)
        #sortedPlaces.append((distanceAway,differenceLat,differenceLng,placeIndex))
        placeObj.setMeetPointInformation(point,distanceAway,differenceLat,differenceLng)
        sortedPlaces.append(placeObj)
        logging.info("place is "+str(distanceAway)+" away from "+str(point))
    sortedPlaces=sorted(sortedPlaces, key=lambda nearPlace: nearPlace.distanceFromPoint)
    logging.info(sortedPlaces[0].name+" is the closest:"+str(sortedPlaces[0].distanceFromPoint))
    return sortedPlaces

def getTravelRadius(poolMember,index,poolLeader,eta):
    logging.info("Getting Places within Travel Radius")
    #walking is 80.49 meters a minute
    #2.7 miles - 54 minutes (lots of traffic lights, basically no hills) = 20 minutes / mile [0]
    #cycling .5 of driving
    #leaderMethodvsMemberMethod=0

    #currently assuming the poolLeader is driving
    #therefor if member is driving then split is 50/50 aka .5
    conversionValue=0
    metersPerMinute=0

    distanceRadius=0
    #below values from online readings
    walkingUrbanMetersPSeconds=1.26
    cyclingUrbanMetersPSeconds=5.27778
    drivingUrbanMetersPSeconds=7.8679

    if(poolMember.methodOfTransport=='driving'):
        distanceRadius=drivingUrbanMetersPSeconds*eta
    elif(poolMember.methodOfTransport=='walking'):
        distanceRadius=walkingUrbanMetersPSeconds*eta
    elif(poolMember.methodOfTransport=='bicycling'):
         distanceRadius=cyclingUrbanMetersPSeconds*eta
    else:
        #stationary
        logging.info(poolMember.name+" is stationary: ("+poolMember.methodOfTransport+")")
        distanceRadius=50



    #if(poolMember.methodOfTransport=='driving'):
    #    metersPerMinute=240
    #    conversionValue=0.5
    #elif(poolMember.methodOfTransport=='walking'):
    #    metersPerMinute=300
    #    conversionValue=0.1
    #elif(poolMember.methodOfTransport=='bicycling'):
   #     metersPerMinute=160
    #    conversionValue=0.25
   # else:
    #    #stationary
    #    logging.info(poolMember.name+" is stationary: ("+poolMember.methodOfTransport+")")
     #   metersPerMinute=0
    #not correct need to do calculations of car vs walking walking vs bike etc
    etaMinutes=eta/60
    #possible distance travled in the eta * the actual distance the person can make it in that time
    #placesRadius=(etaMinutes* metersPerMinute)*conversionValue
    logging.info(poolMember.name+" can travel "+str(distanceRadius)+" meters")
    return distanceRadius

def findFirstOverLappingPointForMember(memberPolyline, leaderLegToNextMember):
    logging.info("Get OverlappingPoint Index")
    memberPoints=get_points_from_polyline(memberPolyline)
    leaderPoints=get_points_from_leg(leaderLegToNextMember)
    memberIndex=0
    leaderIndex=0
    while len(memberPoints)>(memberIndex+1):
        while len(leaderPoints)>(leaderIndex+1):
             if(intersect(memberPoints[memberIndex],memberPoints[memberIndex+1],leaderPoints[leaderIndex],leaderPoints[leaderIndex+1])):
                logging.info("First Intersecting Point at "+str(memberPoints[memberIndex+1]))
                print("intersect")
                return (memberIndex+1), memberPoints
             elif(memberPoints[memberIndex]==leaderPoints[leaderIndex]):
                logging.info("First Equal Point at "+str(memberPoints[memberIndex]))
                print("equal")
                return (memberIndex), memberPoints
             #print(str(memberPoints[memberIndex])+str(leaderPoints[leaderIndex]))
             leaderIndex+=1
        memberIndex+=1
        leaderIndex=0

    logging.info("Failed to find a matching point")
    return None, None

def findFirstOverLappingPointForMember2(memberPolyline, leaderRoute):
    logging.info("Get OverlappingPoint Index")
    memberPoints=get_points_from_polyline(memberPolyline)
    leaderPoints=get_points_from_polyline(leaderRoute)
    memberIndex=0
    leaderIndex=0
    while len(memberPoints)>(memberIndex+1):
        while len(leaderPoints)>(leaderIndex+1):

             if(memberPoints[memberIndex]==leaderPoints[leaderIndex]):
                logging.info("First Equal Point at "+str(memberPoints[memberIndex]))
                print("equal")
                return (memberIndex), memberPoints
             elif(intersect(memberPoints[memberIndex],memberPoints[memberIndex+1],leaderPoints[leaderIndex],leaderPoints[leaderIndex+1])):
                logging.info("First Intersecting Point at "+str(memberPoints[memberIndex+1]))
                print("intersect")
                return (memberIndex), memberPoints
             #print(str(memberPoints[memberIndex])+str(leaderPoints[leaderIndex]))
             leaderIndex+=1
        memberIndex+=1
        leaderIndex=0

    logging.info("Failed to find a matching point")
    return None, None


def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)
