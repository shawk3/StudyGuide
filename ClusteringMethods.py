# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:17:42 2020

@author: shawk
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random



### Helper methods, you can use this or write your own.

def distanceSquared(x,y):
    #Euclidean distance squared.
    dimensionalDistances = [(x[i] - y[i])**2 for i in range(len(x))]
    return sum(dimensionalDistances)


def makeDistanceMatrix(data):
    distanceTriangle = [] #This will look like a lower diagnol matrix
    for i in range(1,len(data)): #for each instance but the first
        distances = [] #this will be a list of distances to location i
        for j in range(0,i): #only need to measure distance for objects before i
            distances.append(distanceSquared(data.iloc[i], data.iloc[j]))
        distanceTriangle.append(distances)
    return distanceTriangle
    # print(data)
    
def newDistance(x, y, technique, xlen, ylen):
    if technique == 's':
        return min(x,y)
    if technique == 'c':
        return max(x,y)
    if technique == 'a':
        return (x*xlen + y*ylen)/(xlen + ylen)
    
    
def updateMatrix(distances, i, j, technique, ilen, jlen):
    #create a new row
    row = []
    n = len(distances)+1
    for col in range(n):
        if col == i+1 or col == j:
            continue
        if col > i+1:
            row.append(newDistance(distances[col - 1][i+1], distances[col-1][j], technique, ilen, jlen))
        elif col > j:
            row.append(newDistance(distances[i][col], distances[col-1][j], technique, ilen, jlen))
        else:
            row.append(newDistance(distances[i][col], distances[j-1][col], technique, ilen, jlen))        
    
    #delete old cols
    for r in range(i+1,n-1):
        del distances[r][i+1]
    for r in range(j,n-1):
        del distances[r][j]
    #delete old rows
    del distances[i]
    del distances[max(j-1,0)]
    
    #Add row to Table
    distances.append(row)
    return distances
       

def updateGroups(groups, i, j):
    #Combine two groups
    #because table excludes first row add one to i when accessing groups which doesn't exclude first row
    newGroup = groups[i+1]+groups[j]
    #remove the old groups, start with higher number
    del groups[i+1]
    del groups[j]
    #add in the new group
    groups.append(newGroup)
    return groups

def hierarchicalClustering(data, k, technique):
    groups = [[name] for name in data.index]
    distances = makeDistanceMatrix(data)
    n = len(groups)
    while n > k:
        #find the index of the minimum distance from table
        minRow = min(distances,key = min)
        i = distances.index(minRow)
        minValue = min(minRow)
        j = minRow.index(minValue)
        
        distances = updateMatrix(distances, i, j, technique, len(groups[i+1]), len(groups[j]))
        groups = updateGroups(groups, i, j)
        n = len(groups)
    return groups  
        

def kMeans(data, k):    
    centroids = [[random.uniform(min(data[c]), max(data[c])) for c in data.columns] for i in range(k)]
    colNum = len(data.columns)
        
    anyChanges = True
    
    while anyChanges:
        anyChanges = False
        
        groups = []
        for i in range(k):
            groups.append([])

        
        for name in data.index:
            distances = [distanceSquared(data.loc[name], c) for c in centroids]
            i = distances.index(min(distances))
            groups[i].append(name)
        
        # plt.scatter([c[0] for c in centroids], [c[1] for c in centroids])
        # for g in groups:
        #     groupData = [[data.loc[name][col] for name in g] for col in data.columns]
        #     plt.scatter(groupData[0], groupData[1])
        # plt.show()
        
            
        for i in range(len(centroids)):
            if not len(groups[i]) == 0:
                average = [0]*colNum
                for name in groups[i]:
                    for c in range(colNum):
                        average[c] += data.loc[name][c]
                
                for c in range(colNum):
                    average[c] = average[c] / len(groups[i])
                    if np.abs(centroids[i][c] - average[c]) > 0.0000001:
                        anyChanges = True
                centroids[i] = average
            
    return groups
        
    

if __name__ == '__main__':       
        
    
    ### Start Program and open file
    print("\nKyle's(Your name Here) Clustering Program.\n")
    filename = input("Please enter the data-file's name: ")
    #filename = "students.csv"
    dataFile = pd.read_csv(filename, index_col = 0)
    
    ### Allow User to select attribute
    print("Here is a list of attributes:")
    for name in dataFile.columns:
        print(name, end = "    ")
    print("\n\nWould you like to perform one dimensional clustering or two?")
    dim = int(input("Type 1 or 2:  "))
    
    if dim == 1:
        attribute = input("\nWhich attribute would you like to cluster?  ")
        #attribute = 'Weight'
        data = dataFile[[attribute]]
        maximum = max(data[attribute])
        minimum = min(data[attribute])
        width = (maximum - minimum)/20
        bins=np.arange(minimum, maximum + width, width)
    elif dim == 2:
        attribute1 = input("Your first attribute:  ")
        attribute2 = input("Your second attribute: ")
        data = dataFile[[attribute1, attribute2]]
    
    ### Potentially plot data
    toPlot = input("Would you like to plot this data? (y,n)  ")
    # toPlot = 'y'
    if toPlot.lower()[0] == 'y':
        if dim == 1:
            plt.hist(data[attribute], bins = bins)
        elif dim == 2:
            plt.scatter(data[attribute1], data[attribute2])
        plt.show()
    #print(data)
        
    ### Select the Clustering Technique
    print("\nWhich clustering technique would you like to use?")
    print("(S)ingle linkage\n(C)omplete linkage\n(A)verage linkage\n(K)-means")
    clusterTechnique = input().lower()
    #clusterTechnique = 's'
    k = int(input("How many clusters? "))
    # k = 5
    
    if clusterTechnique == 'k':
        groups = kMeans(data,k)
    else:
        groups = hierarchicalClustering(data, k, clusterTechnique)
    
    print("The groups are:")
    for g in groups:
        print()
        for name in g:
            print(name)
    #toPlot = input("Would you like to plot the groups? (y/n)  ")
    #toPlot = toPlot.lower()[0]
    
    if toPlot == 'y':
        for g in groups:
            if dim == 1:
                groupData = [data.loc[name][attribute] for name in g]
                plt.hist(groupData, bins = bins)
            elif dim == 2:
                X = [data.loc[name][attribute1] for name in g]
                Y = [data.loc[name][attribute2] for name in g]
                plt.scatter(X,Y)
        plt.show()
      





    