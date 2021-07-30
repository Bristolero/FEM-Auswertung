import numpy as np
import math
import matplotlib.pyplot as plt


# Lädt Coordinate.txt-Datei ein
filename = './...txt'
data = np.loadtxt(filename)

# Splittet Data in zwei Seperate Arrays für x- und y-Werte (ich komme damit besser klar)
x_values = np.array(data[:,0])
y_values = np.array(data[:,1])

# Subtrahiere von allen y_values den folgenden Wert welcher auch als Höhe des Werkstücks definiert wurde 
null_line = 0.15

# Gibt den Index des niedrigsten Punktes wieder
def getSplitIndex():
    a = np.array(y_values)
    lowest = a.min()
    result = np.where(a == lowest)
    return result

# Für die Berechnungen des seitlichen Schnittwinkels: 
angle_value1 = 144
angle_value2 = 185



# Hier wird der Index definiert an dem ein Split stattfinden soll um Aufwürfe links und rechts seperat zu betrachten
splitIndex = getSplitIndex()[0][0]


#Aufwurfbreite wird später in der Methode trapz_positive bestimmt
plough_broadness1 = 0.0
plough_broadness2 = 0.0


# Ändert die Werte von x,y auf Mikrometer-Bereich
for values in range(len(y_values)):
    y_values[values] = (y_values[values] - null_line)*1000

#for i in range(len(y_values)):  
    #print(str(i) + ' y: ' + str(y_values[i]))

for values in range(len(x_values)):
    x_values[values] = x_values[values]*1000

#print(x_values)

#Tiefe des tiefsten Punktes in Mikrometer
depth_of_cut = abs(min(y_values))
print('Einschnitttiefe: ' + str(depth_of_cut))

## Gibt die insgesamt entfernte Fläche zurück (Integration aller negativen Werte)
# x: x-Werte | y: y-Werte | **kwargs: 2 optionale Parameter für Start und Endindex
def calculate_removedArea(x,y, **kwargs):
    print('Calculating removed area: \n')
    removedArea = 0.0
    for i in range(len(x)-1):
       if y[i] < 0: 
           removedArea = removedArea + y[i] * (x[i+1] - x[i])
           #print('Index: ' + str(i) + ' | ' + str(x[i]) + ' | ' +  str(removedArea))
    return round(abs(removedArea),5)
    

## Gibt die Fläche welche durch Aufwürfe enstanden sind zurück (Integration aller positiven Werte)
def calculate_upheavalArea(x,y, **kwargs):
    print('Calculating upheaval area: \n')
    global upheaval1
    global upheaval2
    upheaval1 = 0.0
    upheaval2 = 0.0
    for i in range(0,splitIndex):
        if y[i] > 0: 
            upheaval1 = upheaval1 + y[i] * (x[i+1] - x[i])
            #print('Index: ' + str(i) + ' | ' + str(x[i]) + ' | ' +  str(upheaval1))
    print("Aufwurf 1: " + str(round(upheaval1,5)))
    for i in range(splitIndex, len(x)-1):
        if y[i] > 0: 
            upheaval2 = upheaval2 + y[i] * (x[i+1] - x[i])
            #print('Index: ' + str(i) + ' | ' + str(x[i]) + ' | ' +  str(upheaval2))
    print("Aufwurf 2: " + str(round(upheaval2,5)))
    upheavalArea = upheaval1 + upheaval2
    return round(upheavalArea,5)

## Gibt den Spanwinkel zurück zwischen zwei Werten zurück
def calculate_angle(val1,val2):
    index1 = 0
    index2 = 0
    for i in range(len(x_values)):
        if val1 < x_values[i]:
            index1 = i
            break
    for i in range(len(x_values)):
        if val2 < x_values[i]:
            index2 = i
            break
    print("\nEingelesene Werte zur Berechnung des Schnittwinkels: ")
    print('Start index: ' + str(index1) +  ' Values: ' + str(x_values[index1]) + ' | ' + str(y_values[index1]))
    print('End index: ' + str(index2) +  ' Values: ' + str(x_values[index2]) + ' | ' + str(y_values[index2]))
    
    #Klassiche Winkelberechnung über Hypotenuse und Katheten
    ankathete = abs(y_values[index1] - y_values[index2])
    gegenkathete = abs(x_values[index1] - x_values[index2])
    hypotenuse = math.sqrt(math.pow(ankathete,2) + math.pow(gegenkathete,2))
    #print(hypotenuse)
    angle = math.acos(gegenkathete/hypotenuse)
    print('Angle of cut: ' + str(round(math.degrees(angle),5)))

## Integriert die Fläche über die Trapezoid Regel
# y: y-Werte, x: x-Werte, positive: Positive Werte oder Negative Werte integrieren?

# Aufwürfe per Trapezoidregel. Gibt außerdem die Breite der einzelnen Aufwürfe zurück
def trapz_positive(y,x):
    yCopy = np.copy(y)
    xCopy = np.copy(x)
    for i in range(0, len(x)-1):
        if yCopy[i] <= 0.0:
            yCopy[i] = 0.0
    r, t, s, u = 0, 0, 0, 0

    for j in range(len(xCopy)):
        if yCopy[j]>0.0:
            r = j
            break
    for k in range(r,len(xCopy)):
        if yCopy[k]==0.0:
            t = k
            break
    for l in range(t,len(xCopy)):
        if yCopy[l]>0.0:
            s = l
            break 
    for m in range(s,len(xCopy)):
        if yCopy[m]==0.0:
            u = m
            break     
    global plough_broadness1 
    global plough_broadness2 
    plough_broadness1 = x_values[t]-x_values[r]
    plough_broadness2 = x_values[m]-x_values[l]
    print("Aufwurf 1 Breite: " + str(plough_broadness1))
    print("Aufwurf 2 Breite: " + str(plough_broadness2))
    return np.trapz(yCopy, xCopy)


# Entfernte Fläche mit Hilfe der Trapezoidregel
def trapz_negative(y,x):
    yCopy = np.copy(y)
    xCopy = np.copy(x)
    for i in range(len(xCopy)-1):
        if yCopy[i] >= 0.0:
            yCopy[i] = 0.0
    return abs(np.trapz(yCopy, xCopy))

#Gibt Informationen über Aufwurfhöhe und mittlere Aufwurfhöhe
def ploughInfo():
    max1, max2 = 0, 0
    for i in range(splitIndex):
        if y_values[i] > max1:
            max1 = y_values[i]
    for j in range(splitIndex,len(x_values)):
        if y_values[j] > max2:
            max2 = y_values[j]
    print("Maximalhöhe von Aufwurf 1: " + str(max1))
    print("Maximalhöhe von Aufwurf 2: " + str(max2))
    print("Mittlere Aufwurfbreite 1: " + str(upheaval1/max1))
    print("Mittlere Aufwurfbreite 2 : " + str(upheaval2/max2))





print("Dateiname: " + filename)
#Ausgeben von Werten und Testen der Funktionen
totalRemovedArea = calculate_removedArea(x_values,y_values)
totalUpheavalArea = calculate_upheavalArea(x_values,y_values)

## Flächen

print('Entfernte Fläche in Quadratmikrometer = ' + str(totalRemovedArea))
print('Aufgeworfene Fläche in Quadratmikrometer = ' + str(totalUpheavalArea))
ratio = round(totalUpheavalArea/totalRemovedArea,5) 
print('Verhältnis Aufwürfe zu Entfernter Fläche: ' + str(ratio))

## Winkel

calculate_angle(angle_value1,angle_value2)

#Ausgeben von Werten mit Trapezoidintegration
trapzRemoved = round(trapz_negative(y_values, x_values),5)
trapzUpheaval = round(trapz_positive(y_values, x_values),5)
#print('Entfernte Fläche mit Trapezoidregel = '  + str(trapzRemoved))
#print('Aufgeworfene Fläche mit Trapezoidregel = '  + str(trapzUpheaval))
#ratio2 = round(trapzUpheaval/trapzRemoved,5)
#print('Verhältnis Aufwürfe zu entfernter Fläche mit Trapezoidregel: ' + str(ratio2))

## Info über Aufwürfe

print(ploughInfo())


## Plotte Koordinaten mit plt.plot()
fig = plt.figure(figsize=(15,5))
plt.plot(x_values,y_values)
#plt.xticks(np.arange(min(x_values), max(x_values), 10))
plt.xlabel("Werkstückbreite im μm")
plt.ylabel("Profilhöhe in μm")
plt.show()