import numpy as np
import math
import statistics
from sympy.solvers import solve
from sympy import Symbol

#Zu analysierende Datei
filename = "./rohr3.inp"

#Die Schnitttiefe in Mikrometer
ae = 5
ae = ae/1000

# Die inp.-Files der Simulation mit rotiertem Korn sind identisch mit denen der Standardausrichtung
# Deswegen muss die Rotation noch implementiert werden, da sonst die eingreifenden Normalvektoren nicht richtig erfasst werden
# Dafür sollte der Ursprungsarray mit allen Elementen jeweils um 90/180/270 rotiert werden vor der Auswertung
# Dies ist sehr wichtig und MUSS noch implementiert werden
# Vermutlich vorerst nur 0, 90, 180, 270 implementieren
rotation = 0


## EINLADEN ALLER DATEN
 
#  Lädt alle Nodes der Input-Datei
def getNodes():
    with open(filename, 'r') as f:
        lines = f.readlines()
    # get starting row
    search_start = '*Node'
    search_end = '*Element, type=R3D3'
    start_index = []
    end_index = []
    for line in lines:
        if search_start in line:
            line_start_index = lines.index(line)
            start_index.append(line_start_index+2)
        if search_end in line:
            line_end_index = lines.index(line)
            end_index.append(line_end_index)
        else:
            pass
    # non = number of nodes
    non = end_index[0] - start_index[0]
    #print('Number of nodes: '+str(non))
    # load data from .inp
    node_data = np.loadtxt(filename, skiprows=start_index[0]-1, max_rows=non, delimiter=',', 
        dtype={   'names': ['index', 'x', 'y', 'z'] ,'formats':[np.int, np.float, np.float, np.float ]} )
    np.array(node_data)
    return node_data

## Gibt alle Korndreiecksflächen in Form der Elemente an
def getElements():
    with open(filename, 'r') as f:
        lines = f.readlines()
    # get starting row
    search_start = '*Element, type=R3D3'
    search_end = '*End Part'
    start_index = []
    end_index = []
    for line in lines:
        if search_start in line:
            line_start_index = lines.index(line)
            start_index.append(line_start_index+2)
        if search_end in line:
            line_end_index = lines.index(line)
            end_index.append(line_end_index)
        else:
            pass
    # noe = number of elements
    noe = end_index[0] - start_index[0]
    #print('Number of elements: '+str(noe))
    # load data from .inp
    element_data = np.loadtxt(filename, skiprows=start_index[0]-1, max_rows=noe, delimiter=',', 
        dtype={   'names': ['index', 'x', 'y', 'z'] ,'formats':[np.int32, np.int32, np.int32, np.int32 ]} )
    np.array(element_data)
    return element_data

## Rotiert die Nodes
def rotateNodes(nodes, rot):
    if rot == 90:
        for i in range(len(nodes)):
            tmp1 = nodes[i][1]
            tmp2 = nodes[i][2]
            nodes[i][1] = tmp2 * -1
            nodes[i][2] = tmp1
    if rot == 180:
        for i in range(len(nodes)):
            nodes[i][1] = nodes[i][1] * -1
            nodes[i][2] = nodes[i][2] * -1
    if rot == 270:
        for i in range(len(nodes)):
            tmp1 = nodes[i][1]
            tmp2 = nodes[i][2]
            nodes[i][1] = tmp2 
            nodes[i][2] = tmp1 * -1

## GLOBALE VARIABLEN ALLER NODES UND ELEMENTS

nodes = getNodes()
rotateNodes(nodes,rotation)
elements = getElements()


## ERMITTELN RELEVANTER DREIECKSFLÄCHEN UND NODES

# Gibt die Höhe des tiefsten Nodes zurück
def getLowestNode(): 
    data = nodes
    try:   
        lowestPoint = 1.0
        indexAt = 0
        for i in range(len(data)):
            if data[i][3] <= lowestPoint:
                lowestPoint = data[i][3]
                indexAt = i
        #print ("Lowest Point of z-Axis is: " + str(lowestPoint) + " at Index: " + str(indexAt))
        return lowestPoint
    except: 
        return 0

# Gibt alle IDS zurück von Nodes dessen Position sich innerhalb der Zustellung
def getAllRelevantNodes(cuttingDepth):
    data = nodes
    relevantnodes = []
    ref_zAxis = getLowestNode()
    counter = 0
    for i in range(len(data)): #optional: eliminate duplicates
        if data[i][3] <= ref_zAxis + cuttingDepth:
            relevantnodes.append(data[i])
            counter = counter+1
    print("Anzahl relevanater Nodes : " + str(counter))
    return relevantnodes

# Gibt alle Elements und deren Nodes zurück, welche sich im Eingriff befinden
def getAllRelevantElements(relevantNodes):
    elemArray = elements
    relevantelements = []
    for i in range(len(elemArray)):
        for j in range(len(relevantNodes)):
            if elemArray[i][1] == relevantNodes[j][0] or  elemArray[i][2] == relevantNodes[j][0] or  elemArray[i][3] == relevantNodes[j][0]:
                relevantelements.append(elemArray[i])
                break
    print("Anzahl relevanter Elemente: " + str(len(relevantelements)))
    return relevantelements

## ERSTELLT ARRAYS VON NODES UND ELEMENTS WELCHE SICH IM EINGRIFF BEFINDEN

relevantNodes = getAllRelevantNodes(ae)
#print(relevantNodes)

relevantElements = getAllRelevantElements(relevantNodes)
#print(relevantElements)


## HILFSMETHODEN: NODE UND ELEMENT, SELBSTERKLÄREND

def getNodePositionOfID(NodeID):
    NodeArray = nodes
    arr = [0,0,0]
    arr = [NodeArray[NodeID-1][1], NodeArray[NodeID-1][2],NodeArray[NodeID-1][3]]
    return arr
 
def getNodesOfElem(elem):
    elemArray = getElements()
    arr = [0,0,0]
    arr = [elemArray[elem-1][1], elemArray[elem-1][2],elemArray[elem-1][3]]
    return arr

## Methode um 3 Punkte eines Elements zu finden
def get3Pos(elem):
    arr = [(0,0,0),(0,0,0),(0,0,0)]
    elemNodes = getNodesOfElem(elem)
    for i in range(len(arr)):
        arr[i] = getNodePositionOfID(elemNodes[i]) 
    return arr


## BERECHNUNGEN SPANWINKEL UND NORMALVEKTORES

# Methode zur Berechnung eines Normalenvektors eines bestimmten Elements
def calculateNormal(elem):
    points = get3Pos(elem)
    p0, p1, p2 = points
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    ux, uy, uz = u = [x1-x0, y1-y0, z1-z0]
    vx, vy, vz = v = [x2-x0, y2-y0, z2-z0]

    u_cross_v = [uy*vz-uz*vy, uz*vx-ux*vz, ux*vy-uy*vx]

    normal = np.array(u_cross_v)
    return normal

# Wandelt einen Normalenvektor in einen Einheitsvektor um
def normalize_Vector(vector):
    v_hat = vector / (vector**2).sum()**0.5
    return v_hat

# Entfernt alle Normalvektoren in negativer Schnittrichtung
def filterPositiveY(vectorArr):
    r = []
    for i in range(len(vectorArr)):
        if vectorArr[i][1] > 0:
            r.append(vectorArr[i])
    return r


# Erstellt einen Array von allen sich im Eingriff befindenen Normalvektoren
def createNormalVectorArray():
    vectorArray = []
    for i in range(len(relevantElements)):
        vectorArray.append(calculateNormal(relevantElements[i][0]))
        vectorArray[i] = normalize_Vector(vectorArray[i]) 
        vectorArray[i] = np.append(vectorArray[i],int(relevantElements[i][0]))
    vectorArray = filterPositiveY(vectorArray)
    #print(vectorArray)
    return vectorArray

## Winkelberechnungen

# Erstellt einen Array der vorhandenen Spanwinkel
def calculateAngleOfRake(vectorArray):
    angleArray = []
    zVector = [0,0,1]
    for i in range(len(vectorArray)):
        angle = np.arccos(np.clip(np.dot(vectorArray[i][:-1], zVector), -1.0, 1.0))
        angleArray.append(90 - math.degrees(angle))
    return angleArray

# Erstellt Array von Winkeln bezüglich zur x-Achse
def calculateAngle_Xdirection(vectorArray1):
    angleArray1 = []
    xVector = [1,0,0]
    for i in range(len(vectorArray1)):
        angle = np.arccos(np.clip(np.dot(vectorArray1[i][:-1], xVector), -1.0, 1.0))
        angleArray1.append(90 - math.degrees(angle))
    return angleArray1

# Gibt die zwei Winkel zurück, welche sich im Eingriff am Äußeßrsten befinden
def getOutmostAngles_x_direction(vectorArray): 
    xVector = [1,0,0]
    leftAngle = 0.0
    rightAngle = 0.0
    minPos = 0.0
    maxPos = 0.0
    minIndex = 0
    maxIndex = 0
    for i in range(len(vectorArray)):
        tmp1 = get3Pos(int(vectorArray[i][3]))
        if tmp1[0][0]<minPos or tmp1[1][0]<minPos or tmp1[2][0]<minPos:
            minPos = min(tmp1[0][0],tmp1[1][0],tmp1[2][0])
            minIndex = int(vectorArray[i][3])
            leftAngle = 90 - math.degrees(np.arccos(np.clip(np.dot(vectorArray[i][:-1], xVector), -1.0, 1.0)))
        if tmp1[0][0]>maxPos or tmp1[1][0]>maxPos or tmp1[2][0]>maxPos:
            maxPos = max(tmp1[0][0],tmp1[1][0],tmp1[2][0])
            maxIndex = int(vectorArray[i][3])
            rightAngle = 90 - math.degrees(np.arccos(np.clip(np.dot(vectorArray[i][:-1], xVector), -1.0, 1.0)))
    print("Winkel eingreifendes Element ganz links: " + str(round(leftAngle,5)) + "° | Winkel eingreifendes Element ganz rechts: " + str(round(rightAngle,5)) + "°")

  


## MITTELWERTE EINGREIFENDER SPANWINKEL

def averageAngle(arr):
    return round(sum(arr) / len(arr),5)

def medianAngle(arr):
    return round(statistics.median(arr),5)


## GEWICHTUNG DER SPANWINKEL

# Ermittlung der eingreifenden Dreiecksflächen in projeziert auf die y-Achse
def get2DprojectionArea(elem):
    positions = get3Pos(elem)
    yLimit = getLowestNode() + ae      ## 0.003733 + 0.00625 = 0.009983
       
    point1 = [positions[0][0],positions[0][2]]
    point2 = [positions[1][0],positions[1][2]]
    point3 = [positions[2][0],positions[2][2]]
    #print(str(elem) + " Element | Vorher eingreifende Fläche: " + str(abs(0.5*( (point1[0]*(point2[1]-point3[1])) + (point2[0]*(point3[1]-point1[1])) + (point3[0]*(point1[1]-point2[1])) ) * 1000000)))
    lowestPoint = min(point1[1],point2[1], point3[1])
    lowestPosition = []
    if lowestPoint == point1[1]:
        lowestPosition = point1
        point2 = changePositions(lowestPosition,point2,yLimit)
        point3 = changePositions(lowestPosition,point3,yLimit)
    if lowestPoint == point2[1]:
        lowestPosition = point2
        point1 = changePositions(lowestPosition,point1,yLimit)
        point3 = changePositions(lowestPosition,point3,yLimit)
    if lowestPoint == point3[1]:
        lowestPosition = point3
        point1 = changePositions(lowestPosition,point1,yLimit)
        point2 = changePositions(lowestPosition,point2,yLimit)

    #Area =1/2[x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)]
    area = 0.5*( (point1[0]*(point2[1]-point3[1])) + (point2[0]*(point3[1]-point1[1])) + (point3[0]*(point1[1]-point2[1])) ) * 1000000
    return abs(area)

# Findet den Punkt auf der Geraden welcher die y_Achse scheidet welche durch die Werkstückkante definiert ist | Hilfsmethode
def changePositions(p1, p2, yLimit):
    vector = [p2[0] - p1[0], p2[1] - p1[1]]
    r = Symbol('r')   
    x = Symbol('x')
    if p2[1]<yLimit:
        return p2
    phi = solve(p1[1] + r*vector[1] - yLimit,r)
    new_X = solve(p1[0] + phi[0]*vector[0] -x  ,x)
    return [new_X[0], yLimit]

# Gibt die Gewichtungen der Elemente zurück, d.h. mit welchen Anteil sie in Prozent beim Eingriff beteiligt sind
def findWeighting(elemArray):
    areaValues = []
    weight = []
    for i in range(len(elemArray)):
        areaValues.append(get2DprojectionArea(elemArray[i]))
        #print(areaValues[i])
    sumOfValues = sum(areaValues)
    for j in range(len(areaValues)): 
        weight.append(areaValues[j]/sumOfValues)
    return weight

def trueAverage(angles, weights):
    angleSum = 0.0
    for i in range(len(angles)):
        angleSum = angleSum + (angles[i] * weights[i])
        #print(angleSum)
    return angleSum




##
# Prints und Ausgaben
normalVectorArray = createNormalVectorArray()

#Array der Element-Ids im Eingriff
elems = []
for a in range(len(normalVectorArray)):
    elems.append(int(normalVectorArray[a][3]))

#Legt Gewichtung der Dreiecksflächen fest
weight = findWeighting(elems)

# Berechnung der einzelnen Spanwinkel
angleOfRakeArray = calculateAngleOfRake(normalVectorArray)
x_directionAngleArray = calculateAngle_Xdirection(normalVectorArray)


print("Eingreifende Normalvektoren:                    |     Eingreifende Spanwinkel: ")
for i in range(len(angleOfRakeArray)):
    print(str(normalVectorArray[i]) + "    | " + str(angleOfRakeArray[i]) + "°")

print("Winkel in positiver oder negativer x-Richtung: ")
for j in range(len(x_directionAngleArray)):
    print(str(x_directionAngleArray[j]))

print(" ")
print("Durchschnittlicher Spanwinkel: " + str(averageAngle(angleOfRakeArray)) + "°")
print("Median Spanwinkel: " + str(medianAngle(angleOfRakeArray)) + "°")
#print("tests:")
print(" ")
getOutmostAngles_x_direction(normalVectorArray)
print(" ")
print("Durchschnittlicher Winkel in x-Richtung: " + str(averageAngle(x_directionAngleArray)) + "°")
print("Median Winkel in x-Ricthung " + str(medianAngle(x_directionAngleArray)) + "°")



print("Gewichteter Durchschnittspanwinkel: " + str(trueAverage(angleOfRakeArray, weight)) + "°")
print("Gewichteter Durchschnitts x-Winkel: " + str(trueAverage(x_directionAngleArray,weight)) + "°")