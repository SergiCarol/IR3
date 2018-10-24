#!/usr/bin/python

from collections import namedtuple
import time
import sys
import numpy as np

#  import cProfile


class Edge:
    def __init__(self, origin=None):
        self.origin = None  # write appropriate value
        self.weight = 1  # write appropriate value

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

    # write rest of code that you need for this class


class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0   # write appropriate value
        self.pageIndex = 0
        self.listIndex = 0

    def __repr__(self):
        return "{0}\t{2}\t{1}".format(self.code, self.name, self.pageIndex)

    def __eq__(self, code):
        if isinstance(code, str):
            return self.code == code
        return False


edgeList = []  # list of Edge
edgeHash = dict()  # hash of edge to ease the match
airportList = []  # list of Airport
airportHash = dict()  # hash key IATA code -> Airport


def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r")
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5:
                raise Exception('not an IATA code')
            a.name = temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code = temp[4][1:-1]
            a.listIndex = cont
        except Exception as inst:
            continue
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print("There were {0} Airports with IATA code".format(cont))


def readRoutes(fd):
    print("Reading Routes file from {0}".format(fd))
    routesTxt = open(fd, "r")
    for line in routesTxt.readlines():
        e = Edge()
        temp = line.split(',')
        origin = temp[2]
        destination = temp[4]
        if (airportHash.get(destination) is None or
                airportHash.get(origin) is None):
            continue

        route = edgeHash.get(origin + destination)
        if route is None:
            e.origin = origin
            edgeHash[origin + destination] = e
            dest_airport = airportHash[destination]
            dest_airport.routes.append(e)
            #  dest_airport.routeHash[]
            airportHash[origin].outweight += 1

        else:
            route.weight += 1


def computePageRanks(x=1):
    n = len(airportList)
    L = 0.9
    P = [1.0 / n for _ in range(n)]
    y = 0

    while (y < x):
        if sum(P) != 1:
            print("SUM NOT EQUAL TO 1", sum(P))
        Q = [0 for _ in range(n)]
        for i in range(n):
            s = 0
            for route in airportList[i].routes:
                origin = route.origin
                index = airportHash[origin].listIndex
                s += ((P[index] *
                      route.weight) / airportList[index].outweight)
            Q[i] = L * s + (1 - L) / n
            #print(Q[i])
        P = Q
        y += 1
        print("Iteration", y)
    for i in range(n):
        airportList[i].pageIndex = P[i]
    return x


def outputPageRanks():
    for airport in airportList:
        print(airport)


def compNormWeights():
    for edge in list(edgeHash.values()):
        airport = airportHash[edge.origin]
        edge.weight = edge.weight / airport.outweight


def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    compNormWeights()
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    #outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2 - time1)


if __name__ == "__main__":
    #  cProfile.run('main()')
    main()
