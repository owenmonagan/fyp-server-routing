import logging
from googleAPIRequests import getLatLong

def getPoolMembersMeetLocations(poolMembers):
    logging.info("Get Pool Members Locations")
    locations=[]
    for poolMember in poolMembers:
        if(poolMember.meetPoint==None):
            locations.append(poolMember.origin)
            logging.info(poolMember.name+"locations at "+poolMember.originString)
        else:
            locations.append(poolMember.meetPoint.location)
            logging.info(poolMember.name+"locations at "+poolMember.meetPoint.name)
    return locations


#Organises the poolmembers by first on the route
#future optimisations should change the have the nested loop being the legs instead of the poolmembers
def sortPoolMembersPositionInArrayByRoute(poolMembers, poolDirections):
    logging.info("\n\nSort pool members array by position in route")
    sortedPoolMembers=[]
    legIndex=0
    while (legIndex<len(poolMembers)):
    #for legIndex , leg in enumerate(poolDirections['routes'][0]['legs']:
        leg=poolDirections['routes'][0]['legs'][legIndex]
        logging.info("Find Member at: "+str(leg['end_location']['lat'])+","+str(leg['end_location']['lng']))
        #print "Find Member at: "+str(leg['end_location']['lat'])+","+str(leg['end_location']['lng'])+"\n\n"
        legLat,legLng=float(leg['end_location']['lat']),float(leg['end_location']['lng'])
        indexOfCorrectPoolMember=0
        #lower the better
        closenessOfCorrectPoolMember=None
        for index, poolMember in enumerate (poolMembers):
            #THIS NEEDS TO BE REVISED!!!!!

            #memberLat, memberLng=getLatLong(poolMember.origin)
            memberLat, memberLng=poolMember.origin
            #print poolMember.name
            #print memberLat
            #print memberLng
            closeness=abs(legLat-memberLat)+abs(legLng-memberLng)
            #print closeness
            #print type(closeness)

            if closeness<closenessOfCorrectPoolMember or closenessOfCorrectPoolMember== None:
                closenessOfCorrectPoolMember=closeness
                indexOfCorrectPoolMember=index
                #print str(closeness)+"is better than"+str(closenessOfCorrectPoolMember)

        logging.info("found closest at "+str(poolMembers[indexOfCorrectPoolMember].origin))
        sortedPoolMembers.append(poolMembers[indexOfCorrectPoolMember])
        legIndex+=1 #incriment

    logging.info("sortPoolMembersPositionInArrayByRoute completed:"+str(sortedPoolMembers))
    return sortedPoolMembers