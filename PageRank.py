#!/usr/bin/python

from collections import namedtuple
import time
import sys
import numpy as np

#  import cProfile


class Edge:
    def __init__(self, origin=None):
        self.origin = None  # write appropriate value
        self.weight = 1.0  # write appropriate value
        self.index = 0

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)

    # write rest of code that you need for this class


class Airport:
    def __init__(self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = []
        self.routeHash = dict()
        self.outweight = 0.0   # write appropriate value
        self.pageIndex = 0.0
        self.listIndex = 0.0

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
            dest_airport = airportHash[destination]
            e.origin = origin
            e.index = len(dest_airport.routes)
            edgeHash[origin + destination] = e
            dest_airport.routes.append(e)

        else:
            route.weight += 1.0
        airportHash[origin].outweight += 1.0


def computePageRanks(x=250):
    n = len(airportList)
    L = 0.2
    P = [1.0 / n] * n
    y = 0
    pre_l = ((1.0 - L) / n)
    no_outs = filter(lambda x: x.outweight == 0, airportList)
    num_no_outs = len(list(no_outs))
    # In this case we can consider L to be 0, for nodes with
    # no out edges: https://stackoverflow.com/questions/21507375/how-does-pageranking-algorithm-deal-with-webpage-without-outbound-links
    # thus we are left with noOuts/n
    norm = 1 / n
    # Eq: L * Pr(of No outs) which gives the Pr of one node with no out degree
    prNoOut = L * num_no_outs / n
    while (y < x):
        if not 0.99 <= sum(P) <= 1.05:
            print("SUM NOT EQUAL TO 1", sum(P))
        Q = [0.0] * n
        for i in range(n):
            s = 0
            for route in airportList[i].routes:
                origin = route.origin
                index = airportHash[origin].listIndex
                out = airportHash[origin].outweight
                w = route.weight

                s += P[index] * w / out
            # We add the PR from all the other no outs vertex
            Q[i] = L * s + pre_l + (norm * prNoOut)
        # new page rank considering all vertex go to all vertex,
        # just calulating the jumping part since is what we are interested
        # with 0 out degree we have no page rank per se (norm * prNoOuts)
        norm = (norm * prNoOut) + pre_l   # Recalculate PR of no outs
        P = Q
        y += 1
        print("Iteration", y)
    for i in range(n):
        airportList[i].pageIndex = P[i]
    return x


def outputPageRanks():
    for airport in airportList:
        print(airport)


def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2 - time1)


if __name__ == "__main__":
    #  cProfile.run('main()')
    main()
