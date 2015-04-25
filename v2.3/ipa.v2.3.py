import networkx as nx
import numpy as nm
from gurobipy import *
import matplotlib.pyplot as py
import math as ma
from random import randint


def extractGraph(graph, Z_V):
	edges = list()
	for node in graph.nodes():
		if node not in Z_V:
			edges.append((node,graph.node[node]['mark'][0][0][0]))
			edges.append((node,graph.node[node]['mark'][1][0][0]))
	return edges

def testIn(data1, data2):
	tmp = set(data1).intersection((set(data2)))
	if nm.size(list(tmp)) > 0:
		return True
	return False

def recalculateTime(complete_graph, graph, node_from, source_node):
	window_size = 0
	ret = graph.copy()
        last_node = source_node
        while True:
                if node_from == source_node:
                        window_size += complete_graph.edge[last_node][node_from]['length']
			break
                #print(node_from,graph.node[node_from]['mark'][0][0],graph.node[node_from]['mark'][1][0])
                if graph.node[node_from]['mark'][0][0] != last_node:
                        window_size += complete_graph.edge[last_node][node_from]['length']
			ret.node[node_from]['window'] = window_size
			last_node = node_from
                        node_from = graph.node[node_from]['mark'][0][0]
                else:
                        window_size += complete_graph.edge[last_node][node_from]['length']
			ret.node[node_from]['window'] = window_size
                        last_node = node_from
                        node_from = graph.node[node_from]['mark'][1][0]
        return window_size, last_node, ret

def checkCycle(graph, node_from, node_to, source_node):
	source_count = 0
	last_node = source_node
	while True:
		if node_from == source_node:
			source_count += 1
			break
		#print(node_from,graph.node[node_from]['mark'][0][0],graph.node[node_from]['mark'][1][0])
		if graph.node[node_from]['mark'][0][0] == source_node or graph.node[node_from]['mark'][1][0] == source_node:
			source_count += 1
		if graph.node[node_from]['mark'][0][0] != last_node:
			last_node = node_from
			node_from = graph.node[node_from]['mark'][0][0]
		else:
			last_node = node_from
			node_from = graph.node[node_from]['mark'][1][0]
		if node_from == node_to:
			break
 	return source_count, last_node

def calculateWindowsClarkeWrightRemake(graph, Z_V, window_size):
	ret = nx.Graph()
        K_V = list(set(graph.nodes()) - set(Z_V))
        for node in K_V:
                ret.add_node(node,mark=[list(),list()])
        for node_from in Z_V:
                for node_to in K_V:
                        if 2*graph.edge[node_from][node_to]['length'] <= window_size:
                                ret.node[node_to]['mark'][0].append(node_from)
                                ret.node[node_to]['mark'][1].append(node_from)
	for nodenum in K_V:
		if nm.size(ret.node[nodenum]['mark'][0]) == 0 or nm.size(ret.node[nodenum]['mark'][1]) == 0:
			print('Moc male okno')
			return
	paths = list()
	index = 0
        for node_from in K_V:
                for node_to in K_V:
                        if node_from != node_to:
                                paths.insert(index,(node_from, node_to,graph.edge[node_from][node_to]['length']))
                                index = index + 1
        paths.sort(key=lambda val: val[2])
	while paths:
       	        new_path = paths.pop(0)
		node_list_next = list(set([val for val in ret.node[new_path[0]]['mark'][1]]).intersection(set([val for val in ret.node[new_path[1]]['mark'][1]])))
		node_list_prev = list(set([val for val in ret.node[new_path[0]]['mark'][0]]).intersection(set([val for val in ret.node[new_path[1]]['mark'][0]])))
		savings_next = list()
       	        savings_prev = list()
       	        for nodenum in node_list_next:
                       	save = graph[nodenum][new_path[1]]['length'] + graph[nodenum][new_path[0]]['length'] - graph[new_path[0]][new_path[1]]['length']
               	        #podmienka pre priradovanie vrcholu
                        if save > 0:
                                savings_next.append((new_path[0],new_path[1],nodenum,save))
                for nodenum in node_list_prev:
                        save = graph[nodenum][new_path[1]]['length'] + graph[nodenum][new_path[0]]['length'] - graph[new_path[0]][new_path[1]]['length']
                        #podmienka pre priradovanie vrcholu
                        if save > 0:
                                savings_prev.append((new_path[0],new_path[1],nodenum,save))
                savings_next.sort(key=lambda val: val[3])
                savings_prev.sort(key=lambda val: val[3])
		if nm.size(savings_next) == 0 and nm.size(savings_prev) == 0:
			continue
		#print(new_path[0],new_path[1],nm.size(savings_next))
		if nm.size(savings_next) != 0 and nm.size(savings_prev) == 0:
			save = savings_next.pop(0)
                        if nm.size(ret.node[new_path[0]]['mark'][1]) > 1 or nm.size(ret.node[new_path[1]]['mark'][1]) > 1:
                                ret.node[new_path[0]]['mark'][0] = [save_next[2]]
                                ret.node[new_path[1]]['mark'][1] = [save_next[2]]
                                ret.node[new_path[0]]['mark'][1] = [save_next[2]]
                                ret.node[new_path[1]]['mark'][0] = [save_next[2]]
				ret.node[new_path[0]]['window'] = graph.edge[new_path[0]][save_next[2]]['length']
				ret.node[new_path[1]]['window'] = graph.edge[new_path[1]][save_next[2]]['length']
			continue
	       	if nm.size(savings_prev) != 0 and nm.size(savings_next) == 0:
                        save = savings_prev.pop(0)
                        if nm.size(ret.node[new_path[0]]['mark'][0]) > 1 or nm.size(ret.node[new_path[1]]['mark'][0]) > 1:
                        	ret.node[new_path[0]]['mark'][0] = [save_prev[2]]
                                ret.node[new_path[1]]['mark'][1] = [save_prev[2]]
                                ret.node[new_path[0]]['mark'][1] = [save_prev[2]]
                                ret.node[new_path[1]]['mark'][0] = [save_prev[2]]
				ret.node[new_path[0]]['window'] = graph.edge[new_path[0]][save_next[2]]['length']
				ret.node[new_path[1]]['window'] = graph.edge[new_path[1]][save_next[2]]['length']
			continue
		save_next = savings_next.pop(0)
		save_prev = savings_prev.pop(0)
		if save_next[2] > save_prev[2]:
			if nm.size(ret.node[new_path[0]]['mark'][1]) > 1 or nm.size(ret.node[new_path[1]]['mark'][1]) > 1:
	                      	ret.node[new_path[0]]['mark'][0] = [save_next[2]]
           		        ret.node[new_path[1]]['mark'][1] = [save_next[2]]
				ret.node[new_path[0]]['mark'][1] = [save_next[2]]
				ret.node[new_path[1]]['mark'][0] = [save_next[2]]
				ret.node[new_path[0]]['window'] = graph.edge[new_path[0]][save_next[2]]['length']
				ret.node[new_path[1]]['window'] = graph.edge[new_path[1]][save_next[2]]['length']
		else:
			if nm.size(ret.node[new_path[0]]['mark'][0]) > 1 or nm.size(ret.node[new_path[1]]['mark'][0]) > 1:
	       	                ret.node[new_path[0]]['mark'][0] = [save_prev[2]]
              	        	ret.node[new_path[1]]['mark'][1] = [save_prev[2]]		
				ret.node[new_path[0]]['mark'][1] = [save_prev[2]]
				ret.node[new_path[1]]['mark'][0] = [save_prev[2]]
				ret.node[new_path[0]]['window'] = graph.edge[new_path[0]][save_next[2]]['length']
				ret.node[new_path[1]]['window'] = graph.edge[new_path[1]][save_next[2]]['length']
        paths = list()
        index = 0
        for node_from in K_V:
                for node_to in range(0,node_from):
                        if node_from != node_to:
				if testIn([node_to], Z_V):
					continue
                                paths.insert(index,(node_from, node_to,graph.edge[node_from][node_to]['length']))
                                index = index + 1
        paths.sort(key=lambda val: val[2])
        while paths:
                new_path = paths.pop(0)
		#print('Path',new_path)
		tmp = [ret.node[new_path[0]]['mark'][0],ret.node[new_path[1]]['mark'][0],ret.node[new_path[0]]['mark'][1],ret.node[new_path[1]]['mark'][1]]
		source_node = -1
		start_node = -1
		if ret.node[new_path[0]]['mark'][0][0] == ret.node[new_path[1]]['mark'][0][0] and testIn(ret.node[new_path[0]]['mark'][0], Z_V):
			source_node = ret.node[new_path[0]]['mark'][0][0]
			start_node = new_path[0]
			ret.node[new_path[0]]['mark'][0] = [new_path[1]]
			ret.node[new_path[1]]['mark'][0] = [new_path[0]]
			#print('1',new_path[0],new_path[1])
			#continue
		else:
			if ret.node[new_path[0]]['mark'][0][0] == ret.node[new_path[1]]['mark'][1][0] and testIn(ret.node[new_path[0]]['mark'][0], Z_V):
				source_node = ret.node[new_path[0]]['mark'][0][0]
				start_node = new_path[0]
				ret.node[new_path[0]]['mark'][0] = [new_path[1]]
				ret.node[new_path[1]]['mark'][1] = [new_path[0]]
				#print('2',new_path[0],new_path[1])
				#continue
			else:
				if ret.node[new_path[0]]['mark'][1][0] == ret.node[new_path[1]]['mark'][0][0] and testIn(ret.node[new_path[0]]['mark'][1], Z_V):
					source_node = ret.node[new_path[0]]['mark'][1][0]
					start_node = new_path[1]
					ret.node[new_path[0]]['mark'][1] = [new_path[1]]
					ret.node[new_path[1]]['mark'][0] = [new_path[0]]
					#print('3',new_path[0],new_path[1])
					#continue
				else:
					if ret.node[new_path[0]]['mark'][1][0] == ret.node[new_path[1]]['mark'][1][0] and testIn(ret.node[new_path[0]]['mark'][1], Z_V):
						source_node = ret.node[new_path[0]]['mark'][1][0]
						start_node = new_path[1]
						ret.node[new_path[0]]['mark'][1] = [new_path[1]]
						ret.node[new_path[1]]['mark'][1] = [new_path[0]]
						#print('4',new_path[0],new_path[1])
						#continue
		if source_node != -1:
			if start_node == new_path[0]:
				#print('Run check',new_path[0], new_path[1], source_node)
				count, end = checkCycle(ret, new_path[0], new_path[1], source_node)
				#print('end node:%d'%end)
				if count == 0:
					#break
					#print('revert')
					ret.node[new_path[0]]['mark'][0] = tmp[0]
					ret.node[new_path[1]]['mark'][0] = tmp[1]
					ret.node[new_path[0]]['mark'][1] = tmp[2]
					ret.node[new_path[1]]['mark'][1] = tmp[3]
				else:
					size, end, tmp_g = recalculateTime(graph,ret, end, source_node)
					if size < window_size:
						ret = tmp_g
					else:
						#print('revert')
						ret.node[new_path[0]]['mark'][0] = tmp[0]
						ret.node[new_path[1]]['mark'][0] = tmp[1]
						ret.node[new_path[0]]['mark'][1] = tmp[2]
						ret.node[new_path[1]]['mark'][1] = tmp[3]

			else:
				#print('Run check',new_path[1], new_path[0], source_node)
				count, end = checkCycle(ret, new_path[1], new_path[0], source_node)
				#print('end node:%d'%end)
				if count == 0:
					#break
					#print('revert')
					ret.node[new_path[0]]['mark'][0] = tmp[0]
					ret.node[new_path[1]]['mark'][0] = tmp[1]
					ret.node[new_path[0]]['mark'][1] = tmp[2]
					ret.node[new_path[1]]['mark'][1] = tmp[3]
				else:
					size, end, tmp_g = recalculateTime(graph, ret, end, source_node)
					if size < window_size:
						ret = tmp_g
					else:
						#print('revert')
						ret.node[new_path[0]]['mark'][0] = tmp[0]
						ret.node[new_path[1]]['mark'][0] = tmp[1]
						ret.node[new_path[0]]['mark'][1] = tmp[2]
						ret.node[new_path[1]]['mark'][1] = tmp[3]
	for nodenum in K_V:
		ret.add_edge(nodenum, ret.node[nodenum]['mark'][0][0])
		ret.add_edge(nodenum, ret.node[nodenum]['mark'][1][0])
	return ret.edges(), ret
			


def calculateWindows_ClarkeWright(graph, Z_V, XY, window_size):
	ret = nx.Graph()
	K_V = list(set(graph.nodes()) - set(Z_V))
	for node in K_V:
		ret.add_node(node,mark=[list(),list()])
	for node_from in Z_V:
		for node_to in K_V:
			if graph.edge[node_from][node_to]['length'] <= window_size:
				ret.add_edge(node_from, node_to, length=graph.edge[node_from][node_to]['length'])
				ret.node[node_to]['mark'][0].append((node_from,graph.edge[node_from][node_to]['length']))
				ret.node[node_to]['mark'][1].append((node_from,graph.edge[node_from][node_to]['length']))
	#print(ret.node)
	paths = list()
	index = 0
	for node_from in K_V:
		for node_to in K_V:
			if node_from != node_to:
				paths.insert(index,(node_from, node_to,graph.edge[node_from][node_to]['length']))
				index = index + 1
	paths.sort(key=lambda val: val[2])
	while paths:
		new_path = paths.pop(0)
		#print(new_path)
		node_list_next = list(set([val[0] for val in ret.node[new_path[0]]['mark'][0]]).intersection(set([val[0] for val in ret.node[new_path[1]]['mark'][0]])))
		node_list_prev = list(set([val[0] for val in ret.node[new_path[0]]['mark'][1]]).intersection(set([val[0] for val in ret.node[new_path[1]]['mark'][1]])))
		savings_next = list()
		savings_prev = list()
		for node in node_list_next:
			save = graph[new_path[1]][node]['length'] + graph[node][new_path[0]]['length'] - graph[new_path[0]][new_path[1]]['length']
		#	podmienka pre priradovanie vrcholu
			if save > 0:
				savings_next.append((new_path[0],new_path[1],node,save))
                for node in node_list_prev:
                        save = graph[new_path[1]][node]['length'] + graph[node][new_path[0]]['length'] - graph[new_path[0]][new_path[1]]['length']
                #       podmienka pre priradovanie vrcholu
                        if save > 0:
                                savings_prev.append((new_path[0],new_path[1],node,save))
		savings_next.sort(key=lambda val: val[3])
		savings_prev.sort(key=lambda val: val[3])
		while savings_next or savings_prev:
			if savings_next:
				new_path_next = savings_next.pop(0)
			else:
				new_path_next = [0,0,0,sys.maxint]
	               	if savings_prev:
                                new_path_prev = savings_prev.pop(0)
                        else:
                                new_path_prev = [0,0,0,sys.maxint]
			if new_path_next[3] <= new_path_prev[3] and new_path_next[3] != sys.maxint:	
				if ret.has_edge(new_path_next[1],new_path_next[2]):
					#print('HAS EDGE')
					#print('next',new_path_next)
					ret.remove_edge(new_path_next[1],new_path_next[2])
					ret.node[new_path_next[0]]['mark'][0] = [(new_path_next[1],graph[new_path_next[0]][new_path_next[1]]['length'],new_path_next[2])]
					ret.node[new_path_next[1]]['mark'][0] = [(new_path_next[2],graph[new_path_next[1]][new_path_next[2]]['length'],new_path_next[2])]
					for node in ret.node[new_path_next[0]]['mark'][1]:
						if node[0] in Z_V:
							ret.node[new_path_next[0]]['mark'][1] = [(new_path_next[2],graph[new_path_next[0]][new_path_next[2]]['length'],new_path_next[2])]
							break
					ret.node[new_path_next[1]]['mark'][1] = [(new_path_next[0],graph[new_path_next[0]][new_path_next[1]]['length'],new_path_next[2])]
					if new_path_prev[3] != sys.maxint:
						savings_prev.insert(0,new_path_prev)
					break
                        if new_path_next[3] > new_path_prev[3] and new_path_prev[3] != sys.maxint:         
                                if ret.has_edge(new_path_prev[2],new_path_prev[0]):
                                        #print('HAS EDGE')
                                        print('prev',new_path_prev)
                                        ret.remove_edge(new_path_prev[2],new_path_prev[0])
					if ret.has_edge(new_path_prev[1],new_path_prev[2]):
						#print('remove',new_path_prev[1],new_path_prev[2])
						ret.remove_edge(new_path_prev[1],new_path_prev[2])
					print(new_path_prev[0],'->',new_path_prev[1])
					ret.node[new_path_prev[0]]['mark'][0] = [(new_path_prev[1],graph[new_path_prev[0]][new_path_prev[1]]['length'],new_path_prev[2])]
					print(ret.node[new_path_prev[0]]['mark'][0])
                                        for node in ret.node[new_path_prev[0]]['mark'][1]:
                                                if node[0] in Z_V:                                      
							ret.node[new_path_prev[0]]['mark'][1] = [(new_path_prev[1],graph[new_path_prev[0]][new_path_prev[2]]['length'],new_path_prev[2])]
							print(ret.node[new_path_prev[0]]['mark'][0])
							break
                                        for node in ret.node[new_path_prev[1]]['mark'][0]:
                                                if node[0] in Z_V:                      
		                  			ret.node[new_path_prev[1]]['mark'][0] = [(new_path_prev[1],graph[new_path_prev[1]][new_path_prev[2]]['length'],new_path_prev[2])]
		                        ret.node[new_path_prev[1]]['mark'][1] = [(new_path_prev[0],graph[new_path_prev[0]][new_path_prev[1]]['length'],new_path_prev[2])]
	                                if new_path_prev[3] != sys.maxint:
                                                savings_next.insert(0,new_path_next)
                                        break
			#if new_path_next[3] != sys.maxint and new_path_prev[3] != sys.maxint:
			#	if ret.has_edge(new_path_next[2],new_path_prev[0]):
                                        #print('HAS EDGE')
                                        #print('prev',new_path_prev)
                        #                ret.remove_edge(new_path_next[2],new_path_prev[0])
                        #                if ret.has_edge(new_path_next[1],new_path_prev[2]):
                        #                        #print('remove',new_path_prev[1],new_path_prev[2])
                        #                        ret.remove_edge(new_path_next[1],new_path_prev[2])
                        #                ret.node[new_path_next[0]]['mark'][0] = [(new_path_prev[1],graph[new_path_prev[0]][new_path_prev[1]]['length'],new_path_prev[2])]
                        #                for node in ret.node[new_path_prev[0]]['mark'][1]:
                        #                        if node[0] in Z_V:
                        #                                ret.node[new_path_next[0]]['mark'][1] = [(new_path_prev[1],graph[new_path_prev[0]][new_path_prev[2]]['length'],new_path_prev[2])]
                        #                                print('add_prev',new_path_prev[0],new_path_prev[2],new_path_prev[1])
                       #                                 break
                       #                 for node in ret.node[new_path_prev[1]]['mark'][0]:
                       #                         if node[0] in Z_V:
                       #                                 ret.node[new_path_prev[1]]['mark'][0] = [(new_path_prev[1],graph[new_path_prev[1]][new_path_prev[2]]['length'],new_path_prev[2])]
                       #                 ret.node[new_path_prev[1]]['mark'][1] = [(new_path_prev[0],graph[new_path_prev[0]][new_path_prev[1]]['length'],new_path_prev[2])]
	new_ret = nx.Graph()
	for node in graph.nodes():		
		new_ret.add_node(node)
		new_ret.node[node]['start'] = 0
		new_ret.node[node]['end'] = 0
	for node in K_V:
		new_ret.add_edge(node, int(ret.node[node]['mark'][0][0][0]))		
	#print(ret.node[1]['mark'])
	for node in K_V:
		if new_ret.degree(node) < 2:
			#print(node)
			new_ret.add_edge(node, ret.node[node]['mark'][0][0][0])							
			new_ret.add_edge(node, ret.node[node]['mark'][1][0][0])							
	#for node in Z_V:
	#	n_list = list(new_ret.neighbors(node))
	#	last_node = node
	#	while n_list:
	#		act_node = n_list.pop()
	#		was_path = False
	#		while ret.node[act_node]['mark'][0][0][0] != node:
	#			new_ret.node[act_node]['start'] = new_ret.node[last_node]['start'] + graph.edge[last_node][act_node]['length']
	#			last_node = act_node
	#			act_node = ret.node[act_node]['mark'][0][0][0]
	#			was_path = True
	#		if was_path:
	#			new_ret.node[act_node]['start'] = new_ret.node[last_node]['start'] + graph.edge[last_node][act_node]['length']
	return new_ret, ret, paths		

def drawGraph(edges, sources, coordinates, graph):
	G = nx.Graph()
	G.add_nodes_from(sources)
	G.add_edges_from(edges)
	for node in G.nodes():
	    G.node[node]['color'] = 'r'
	for node in sources:
	    G.node[node]['color'] = 'b'
	labels = {}
	for val in graph.nodes():
			labels[val] = '%d' % (val)
	nx.draw_networkx_nodes(G,pos=coordinates,node_color=[G.node[node]['color'] for node in G],node_size=300)
	nx.draw_networkx_edges(G,pos=coordinates)
	for val in coordinates:
		coordinates[val] = (coordinates[val][0],coordinates[val][1]+0.015)
	nx.draw_networkx_labels(G,pos=coordinates,labels=labels, font_size=15)	
	py.show() 
	
def drawWindowedGraph(w_graph, sources, coordinates, graph, y_offset):
        G = nx.Graph()
        G.add_nodes_from(sources)
        G.add_edges_from(w_graph.edges())
        for node in G.nodes():
            G.node[node]['color'] = 'r'
        for node in sources:
            G.node[node]['color'] = 'b'
        labels = {}
        for val in graph.nodes():
			if testIn([val],sources):
                        	labels[val] = '%d' % (val)
			else:
                        	labels[val] = '%d[%d]' % (val,w_graph.node[val]['window'])
	nx.draw_networkx_nodes(G,pos=coordinates,node_color=[G.node[node]['color'] for node in G],node_size=300)
        nx.draw_networkx_edges(G,pos=coordinates)
        for val in coordinates:
                coordinates[val] = (coordinates[val][0],coordinates[val][1]+y_offset)
        nx.draw_networkx_labels(G,pos=coordinates,labels=labels, font_size=10)
        py.show()

def readGraph(n, m, car_quantities, coordinate_path):
	Z = {}
	Z_V = list()
	G = nx.Graph()
	C_list = nm.loadtxt(coordinate_path)
	XY = {}
	counter = 0
	for (i, x, y) in C_list:
		if(counter >= n):
			break
		XY[int(i)] = (x,y)
		counter += 1
#	G_list = nm.loadtxt(nodes_path)
	for i in XY.keys():
		for j in XY.keys():
			if(i <= j):
				continue
			value = int(ma.sqrt(ma.pow(ma.fabs(XY[i][0]-XY[j][0]), 2)+ma.pow(ma.fabs(XY[i][1]-XY[j][1]), 2)))
			#print value
			G.add_edge(i, j, length=value)
	counter = 0
	i = 0;
	#for i in range(0,m):
	while(len(set(Z)) < m):
		i += randint(1,n)
		#print i % n, XY.keys()[i%n], car_quantities[counter]
		if (XY.keys()[i%n], car_quantities[counter]) in Z.values():
			continue
		Z[counter] = (XY.keys()[i%n], car_quantities[counter])
		Z_V.append(XY.keys()[i%n])
		counter += 1 
	
	return Z,G,XY,Z_V


def solve(Z,G,max_tau,tau):
	model = Model("ipamod")
	
	V_Z = list()  		#Zberne miesta
	P = {}      		#Pocet vozidiel (na indexe zberneho miesta	
	for i in Z:
		V_Z.append(Z[i][0])
		P[Z[i][0]] = Z[i][1]
	V = list(G.nodes()) 		#vrcholy
	V_K = list(set(V) - set(V_Z)) 	#Klienti
	
	c = {}
	for edge in G.edges():
		c[edge[0],edge[1]] = G.get_edge_data(*edge)['length']
		c[edge[1],edge[0]] = G.get_edge_data(*edge)['length']

	x = {}
	for i in V:
		for j in V:
			x[i,j] = model.addVar(ub=1, vtype='B', name="x(%s,%s)"%(i,j))
	u = {}
	for j in G.nodes():
		u[j] = model.addVar(lb=0, ub=max_tau, vtype=GRB.INTEGER, name="u(%s)"%j)
	model.update()

	#prijazd P[j] aut do miesta v V_Z
	for j in V_Z:
		model.addConstr(quicksum(x[i,j] for i in V) == P[j], "Stlpec_j%d"%(j))

	#ku klinetovi prichadzam prave raz
	for j in V_K:
		model.addConstr(quicksum(x[i,j] for i in V if i != j) == 1, "SumaMiesta_j%d"%(j))
	#vyjazd P[j] aut z miesta v V_Z	
	for i in V_Z:
		model.addConstr(quicksum(x[i,j] for j in V) == P[i], "Stlpec_i%d"%(j))

	#od klienta odchadzam prave raz	
	for i in V_K:
		model.addConstr(quicksum(x[i,j] for j in V if i != j) == 1, "SumaMiestai_i%d"%(j))
	
	for i in V:
		for j in V_K:
			if i != j:
				model.addConstr(u[i] - u[j] + (max_tau + c[i,j]+ tau)*x[i,j] <= max_tau, "u_%d_%d"%(i,j))	
	for i in V_K:
		for k in V_Z:
			model.addConstr(c[i,k]*x[i,k] + u[i] + tau <= max_tau, "end_u_%d_%d"%(i,j))	

	for i in V_K:
		model.addConstr(u[i] >= G.node[i]['start'])	
	for i in V_K:
		model.addConstr(u[i] <= G.node[i]['end'])	
	
	for i in V_Z:
		model.addConstr(u[i] == 0)
	
	model.update()

	model.setObjective(quicksum(c[i,j]*x[i,j] for i in V for j in V),GRB.MINIMIZE)

	model.update()

	model.optimize()
	edges = []
	EPS = 1.e-6
	for (i,j) in x:
		if x[i,j].X > EPS:
			edges.append((i,j))
	ret_u = []
	for i in V:
		ret_u.append((i,u[i].X))	
	return model.ObjVal,edges, ret_u
