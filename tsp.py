# encoding:utf-8

'''
	Solution for Travelling Salesman Problem using PSO (Particle Swarm Optimization)
	Discrete PSO for TSP

	References: 
		http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.258.7026&rep=rep1&type=pdf
		http://www.cs.mun.ca/~tinayu/Teaching_files/cs4752/Lecture19_new.pdf
		http://www.swarmintelligence.org/tutorials.php

	References are in the folder "references" of the repository.
'''

from operator import attrgetter
import random, sys, time, copy
import streamlit as st
import numpy as np
import pandas as pd
import altair
import matplotlib.pyplot as plt
import math
import random
import csv


# class that represents a graph
class Graph:

	def __init__(self, amount_vertices):
		self.edges = {} # dictionary of edges
		self.vertices = set() # set of vertices
		self.amount_vertices = amount_vertices # amount of vertices


	# adds a edge linking "src" in "dest" with a "cost"
	def addEdge(self, src, dest, cost = 0):
		# checks if the edge already exists
		if not self.existsEdge(src, dest):
			self.edges[(src, dest)] = cost
			self.vertices.add(src)
			self.vertices.add(dest)


	# checks if exists a edge linking "src" in "dest"
	def existsEdge(self, src, dest):
		return (True if (src, dest) in self.edges else False)


	# shows all the links of the graph
	def showGraph(self):
		#print('Showing the graph:\n')
		for edge in self.edges:
			print('%d linked in %d with cost %d' % (edge[0], edge[1], self.edges[edge]))

	# returns total cost of the path
	def getCostPath(self, path):
		
		total_cost = 0
		for i in range(self.amount_vertices - 1):
			total_cost += self.edges[(path[i], path[i+1])]

		# add cost of the last edge
		total_cost += self.edges[(path[self.amount_vertices - 1], path[0])]
		return total_cost


	# gets random unique paths - returns a list of lists of paths
	def getRandomPaths(self, max_size):

		random_paths, list_vertices = [], list(self.vertices)

		initial_vertice = random.choice(list_vertices)
		if initial_vertice not in list_vertices:
			#print('Error: initial vertice %d not exists!' % initial_vertice)
			sys.exit(1)

		list_vertices.remove(initial_vertice)
		list_vertices.insert(0, initial_vertice)

		for i in range(max_size):
			list_temp = list_vertices[1:]
			random.shuffle(list_temp)
			list_temp.insert(0, initial_vertice)

			if list_temp not in random_paths:
				random_paths.append(list_temp)

		return random_paths


# class that represents a complete graph
class CompleteGraph(Graph):

	# generates a complete graph
	def generates(self):
		for i in range(self.amount_vertices):
			for j in range(self.amount_vertices):
				if i != j:
					weight = random.randint(1, 10)
					self.addEdge(i, j, weight)


# class that represents a particle
class Particle:

	def __init__(self, solution, cost):

		# current solution
		self.solution = solution

		# best solution (fitness) it has achieved so far
		self.pbest = solution

		# set costs
		self.cost_current_solution = cost
		self.cost_pbest_solution = cost

		# velocity of a particle is a sequence of 4-tuple
		# (1, 2, 1, 'beta') means SO(1,2), prabability 1 and compares with "beta"
		self.velocity = []
		

	# set pbest
	def setPBest(self, new_pbest):
		self.pbest = new_pbest

	# returns the pbest
	def getPBest(self):
		return self.pbest

	# set the new velocity (sequence of swap operators)
	def setVelocity(self, new_velocity):
		self.velocity = new_velocity

	# returns the velocity (sequence of swap operators)
	def getVelocity(self):
		return self.velocity

	# set solution
	def setCurrentSolution(self, solution):
		self.solution = solution

	# gets solution
	def getCurrentSolution(self):
		return self.solution

	# set cost pbest solution
	def setCostPBest(self, cost):
		self.cost_pbest_solution = cost

	# gets cost pbest solution
	def getCostPBest(self):
		return self.cost_pbest_solution

	# set cost current solution
	def setCostCurrentSolution(self, cost):
		self.cost_current_solution = cost

	# gets cost current solution
	def getCostCurrentSolution(self):
		return self.cost_current_solution

	# removes all elements of the list velocity
	def clearVelocity(self):
		del self.velocity[:]


# PSO algorithm
class PSO:

	def __init__(self, graph, iterations, size_population, beta=1, alfa=1):
		self.log = open("execution.txt","w");
		self.log.write("init")
		self.graph = graph # the graph
		self.iterations = iterations # max of iterations
		self.size_population = size_population # size population
		self.particles = [] # list of particles
		self.beta = beta # the probability that all swap operators in swap sequence (gbest - x(t-1))
		self.alfa = alfa # the probability that all swap operators in swap sequence (pbest - x(t-1))
		self.generationsSols = []
		#print("init")

		# initialized with a group of random particles (solutions)
		solutions = self.graph.getRandomPaths(self.size_population)
		self.log.write("initialized with a group of random particles (solutions)"+ "\n")
		self.log.write(str(solutions)+ "\n")
		# checks if exists any solution
		if not solutions:
			#print('Initial population empty! Try run the algorithm again...')
			sys.exit(1)

		# creates the particles and initialization of swap sequences in all the particles
		for solution in solutions:
			# creates a new particle
			
			particle = Particle(solution=solution, cost=graph.getCostPath(solution))
			# add the particle
			self.particles.append(particle)
			self.log.write(str(solution) +" cost: "+str(graph.getCostPath(solution)) + "\n")

		# updates "size_population"
		self.size_population = len(self.particles)


	# set gbest (best particle of the population)
	def setGBest(self, new_gbest):
		#print("New Gbest", new_gbest)
		self.gbest = new_gbest

	# returns gbest (best particle of the population)
	def getGBest(self):
		return self.gbest


	# shows the info of the particles
	def showsParticles(self):

		#print('Showing particles...\n')
		for particle in self.particles:
			print('pbest: %s\t|\tcost pbest: %d\t|\tcurrent solution: %s\t|\tcost current solution: %d' \
				% (str(particle.getPBest()), particle.getCostPBest(), str(particle.getCurrentSolution()),
							particle.getCostCurrentSolution()))
		#print('')


	def run(self):

		# for each time step (iteration)
		for t in range(self.iterations):
			print(t)
			self.log.write("iteration: " + str(t)+ "\n")
			#print("iterarion>> ",t)
			# updates gbest (best particle of the population)
			self.gbest = min(self.particles, key=attrgetter('cost_pbest_solution'))
			v  = self.getGBest().getCostPBest()
			self.generationsSols.append(v)
			if t == 1:
				print(t,"intial graph\n")
				fxs = []
				fys = []
				for i in self.getGBest().getPBest():
					fxs.append(xs[i])
					fys.append(ys[i])
				fxs.append(fxs[0])
				fys.append(fys[0])
				fg1 = plt.figure(3)
				plt.plot(fxs,fys)
				fg1.show()
				plt.pause(1)
				
			if t % 20 == 0:
				# print(t,"\n")
				plt.clf()
				fxs = []
				fys = []
				for i in self.getGBest().getPBest():
					fxs.append(xs[i])
					fys.append(ys[i])
				fxs.append(fxs[0])
				fys.append(fys[0])
				fg = plt.figure(1)
				plt.plot(fxs,fys)
				plt.show(block=False)
				
				
				plt.pause(.5)
				# plt.pause(2)
				
				
			
			
			self.log.write("current gbest >> " + str(self.getGBest().getCostPBest())+ str(self.getGBest().getCurrentSolution())+"\n")
			self.log.write(str([j.getCostPBest() for j in self.particles])+ "\n")
			# for each particle in the swarm
			for particle in self.particles:
				lotT  = "particle>> pbest "+ str(particle.getPBest())+" velocity>>" + str(particle.getVelocity())
				self.log.write(lotT+ "\n")
				#print("particle>> pbest", particle.getPBest()," velocity>>", particle.getVelocity())
				particle.clearVelocity() # cleans the speed of the particle
				temp_velocity = []
				solution_gbest = copy.copy(self.gbest.getPBest()) # gets solution of the gbest
				self.log.write("solution gbest>> "+str(self.gbest.getPBest())+"\n")
				solution_pbest = particle.getPBest()[:] # copy of the pbest solution
				solution_particle = particle.getCurrentSolution()[:] # gets copy of the current solution of the particle

				# generates all swap operators to calculate (pbest - x(t-1))
				for i in range(self.graph.amount_vertices):
					if solution_particle[i] != solution_pbest[i]:
						# generates swap operator
						self.log.write("generate swap operator "+str(solution_pbest.index(solution_particle[i]))+", alpha"+str(self.alfa)+" \n")
						
						swap_operator = (i, solution_pbest.index(solution_particle[i]), self.alfa)

						# append swap operator in the list of velocity
						temp_velocity.append(swap_operator)

						# makes the swap
						aux = solution_pbest[swap_operator[0]]
						solution_pbest[swap_operator[0]] = solution_pbest[swap_operator[1]]
						solution_pbest[swap_operator[1]] = aux

				# generates all swap operators to calculate (gbest - x(t-1))
				for i in range(self.graph.amount_vertices):
					if solution_particle[i] != solution_gbest[i]:
						# generates swap operator
						swap_operator = (i, solution_gbest.index(solution_particle[i]), self.beta)

						# append swap operator in the list of velocity
						temp_velocity.append(swap_operator)

						# makes the swap
						self.log.write("swap between: "+str(swap_operator[0])+" and "+str(swap_operator[1])+" \n")
						aux = solution_gbest[swap_operator[0]]
						solution_gbest[swap_operator[0]] = solution_gbest[swap_operator[1]]
						solution_gbest[swap_operator[1]] = aux

				
				# updates velocity
				particle.setVelocity(temp_velocity)

				# print("# generates new solution for particle")
				for swap_operator in temp_velocity:
					if random.random() <= swap_operator[2]:
						# makes the swap
						aux = solution_particle[swap_operator[0]]
						solution_particle[swap_operator[0]] = solution_particle[swap_operator[1]]
						solution_particle[swap_operator[1]] = aux
				
				# updates the current solution
				particle.setCurrentSolution(solution_particle)
				# gets cost of the current solution
				cost_current_solution = self.graph.getCostPath(solution_particle)
				# updates the cost of the current solution
				particle.setCostCurrentSolution(cost_current_solution)

				# checks if current solution is pbest solution
				if cost_current_solution < particle.getCostPBest():
					particle.setPBest(solution_particle)
					particle.setCostPBest(cost_current_solution)
	
		# fig = plt.figure(2)
		# plt.plot([i for i in range(self.iterations)] ,self.generationsSols)
		# fig.show()
		


def ab_len(x1,x2,y1,y2,c1,c2):
    l = math.sqrt((x1-x2)**2+(y1-y2)**2)
    return c1,c2,l

if __name__ == "__main__":
	


	file_name = input("enter the file name: ")
	f = open(file_name+".tsp","r")
	
	while f.readline() != "NODE_COORD_SECTION\n":
		continue

	nOfCities = 0
	cities = []
	ys = []
	xs = []
	line = f.readline()
	while line !="EOF\n":
		print(line)
		nOfCities+=1
		city = str(line).split(" ")
		print(city)
		cities.append(city[0])
		xs.append(float(city[1]))
		nys = city[2]
		nys = nys.replace("\n","")
		ys.append(float(nys))
		line = f.readline()
	
	# f.seek(0)
	# l_sk = int(input("enter the amount of lines to skip: "))
	
	graph = Graph(amount_vertices=nOfCities)
	# f = open(file_name+".tsp","r")
	# for i in range(l_sk):
	# 	print(f.readline())
	
	# for i in range(nOfCities):
	# 	city = str(line).split(" ")
	# 	#print(city)
	# 	cities.append(city[0])
	# 	xs.append(float(city[1]))
	# 	nys = city[2]
	# 	nys = nys.replace("\n","")
	# 	ys.append(float(nys))
	initialGraph = plt.figure(4)
	plt.plot(xs,ys,"bo")
	for i in range(len(cities)):
		x1 = xs[i]
		y1 = ys[i]
		for j in range(len(cities)):
			if j<=i:
				continue
			x2 = xs[j]
			y2 = ys[j]
			res = ab_len(x1,x2,y1,y2,i,j)
			graph.addEdge(i,j,res[2])
			graph.addEdge(j,i,res[2])



	# This graph is in the folder "images" of the repository.
	# graph.showGraph()

	fxs = []
	fys = []


	pso = PSO(graph, iterations=300, size_population=200, beta=1, alfa=1)
	pso.run() # runs the PSO algorithm
	pso.showsParticles() # shows the particles

	# shows the global best particle
	#print('gbest: %s | cost: %d\n' % (pso.getGBest().getPBest(), pso.getGBest().getCostPBest()))

	# r = [str(i),str(j/10),str(k/10),str(pso.getGBest().getCostPBest()),str(pso.getGBest().getPBest())]
	# print(r)
	# writer.writerow(r)
	# print(pso.getGBest()," GBEST", len(pso.getGBest()))
	# print(pso.getGBest().getPBest()," GPBEST ", len(pso.getGBest().getPBest()) )

	# creates a PSO instance

	conv = plt.figure(6)
	plt.plot(fxs,fys)
	plt.clf()
	plt.plot([i for i in range(pso.iterations)] ,pso.generationsSols)
	print("showing", pso.generationsSols)
	conv.show()



	fres = open("fres1.csv","w",newline="")
	writer = csv.writer(fres)
	d =  input("do you want to run it for 800 times ? 1/0")
	if d == '1':
		for i in range(10):
			for j in range(1,10):
				for k in range(1,10):
					pso = PSO(graph, iterations=300, size_population=200, beta=k/10, alfa=j/10)
					pso.run() # runs the PSO algorithm
					pso.showsParticles() # shows the particles

					# shows the global best particle
					#print('gbest: %s | cost: %d\n' % (pso.getGBest().getPBest(), pso.getGBest().getCostPBest()))

					r = [str(i),str(j/10),str(k/10),str(pso.getGBest().getCostPBest()),str(pso.getGBest().getPBest())]
					print(r)
					writer.writerow(r)
					# print(pso.getGBest()," GBEST", len(pso.getGBest()))
					# print(pso.getGBest().getPBest()," GPBEST ", len(pso.getGBest().getPBest()) )
		fres.close()
	for i in range(len(pso.getGBest().getPBest())):
		print("appending")
		fxs.append(xs[i])
		fys.append(ys[i])
	fxs.append(fxs[0])
	fys.append(fys[0])
	
	# conv = plt.figure(4)
	# plt.plot(fxs,fys)
	# plt.clf()
	# plt.plot([i for i in range(pso.iterations)] ,pso.generationsSols)
	# print("showing", pso.generationsSols)
	# conv.show()
	'''
	# random graph
	##print('Random graph...')
	random_graph = CompleteGraph(amount_vertices=20)
	random_graph.generates()
	pso_random_graph = PSO(random_graph, iterations=10000, size_population=10, beta=1, alfa=1)
	pso_random_graph.run()
	##print('gbest: %s | cost: %d\n' % (pso_random_graph.getGBest().getPBest(), 
					pso_random_graph.getGBest().getCostPBest()))
	'''

#TODO read file directly nichan 