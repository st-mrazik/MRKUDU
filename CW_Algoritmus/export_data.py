import numpy as nm
import os as os
import networkx as nx
import math as ma
import random as ra 

def exportDataFromTSP(filename, sources):
	file_name,file_ext = os.path.splitext(filename)
	if not os.path.exists(file_name):
		os.makedirs(file_name)
	file = open(filename,'r')
	for i in range(0,6):
		file.readline()
	line = file.readline()
	data = []
	while line:
		node = line.split()
		data.append([int(node[0])-1,int(node[1]),int(node[2])])
		line = file.readline()
	nm.savetxt(file_name + "/coordinates.txt", data, "%d %f %f")
	distances = []
	for i in range(0,len(data)):
		for j in range(i, len(data)):
			if i == j:
				continue
			distances.append([i,j,ma.sqrt(ma.pow(data[i][1]-data[j][1],2)+ma.pow(data[i][2]-data[j][2],2))])
	nm.savetxt(file_name + "/distances.txt", distances, "%d %d %f")	
	src = []
	for i in range(0,len(sources)):
		src.append([int(i),int(sources[i]),int(0)])
	nm.savetxt(file_name + "/sources.txt", src, "%d %d %d")
	tw = []
	for i in range(0, len(data)):
		tw.append([i,0,0])
	nm.savetxt(file_name + "/timeWindows.txt", tw, "%d %d %d")

def exportData(Z, XY, graph, newDirectory):
	if not os.path.exists(newDirectory):
		os.makedirs(newDirectory)
	dataList = []
	for key in XY.keys():
		dataList.append((key, XY.get(key)[0], XY.get(key)[1]))
	nm.savetxt(newDirectory + "/coordinates.txt", dataList, "%d %f %f")
	dataList = []
	for key in Z.keys():
		dataList.append((key, Z.get(key)[0], Z.get(key)[1]))
	nm.savetxt(newDirectory + "/sources.txt", dataList, "%d %d %d")
	dataList = []
	for (i,j) in graph.edges():
		dataList.append((i,j,graph[i][j]['length']))
	nm.savetxt(newDirectory + "/distances.txt", dataList, "%d %d %d")
	dataList = generateTimeWindows(0,100,100,200,graph.nodes())
	nm.savetxt(newDirectory + "/timeWindows.txt", dataList, "%d %d %d")

def importData(directory):
	Z = {}
	Z_V = []
	X = nm.loadtxt(directory + "/sources.txt")
	for val in X:
		Z[int(val[0])] = (int(val[1]), int(val[2]))
		Z_V.append(int(val[1]))
	XY = {}
	X = nm.loadtxt(directory + "/coordinates.txt")
	for val in X:
		XY[int(val[0])] = (float(val[1]), float(val[2]))
	X = {}
	X = nm.loadtxt(directory + "/distances.txt")
	TW = nm.loadtxt(directory + "/timeWindows.txt") 
	G = nx.Graph()
	for val in TW:
		G.add_node(int(val[0]), start=int(val[1]), end=int(val[2]))
	for val in X: 
		G.add_edge(int(val[0]), int(val[1]), length=int(val[2]))	
	return Z, Z_V, XY, G


def generateTimeWindows(start, start_length, end, end_length, nodes):
	windowList = []
	ra.seed()	
	for node in nodes:
			windowList.append((node, ra.randint(start, start+start_length), ra.randint(end, end+end_length)))
	return windowList

 
def convertDataFromDistanceMatrix(path, dest):
	X = nm.loadtxt(path)
	ret = []
	i = 1
	for val in X:
		P = list(val)
		for j in range(i, len(P)):
			if i == 1:
				print float(P[j])
			ret.append((int(i),int(j+1),float(P[j])))
		i += 1
	nm.savetxt(dest, ret, "%d %d %f")
