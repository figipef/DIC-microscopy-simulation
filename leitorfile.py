import os
import math
pi = math.pi
def ler_dados(path):
	f = open(path, "r")

	dados_x = []
	dados_y = []

	for i in f:
		a = ""
		n = 0
		n1 = 0
		n2 = 0
		for j in i:
			try:
				if j == "-":
					a = a + j
				elif type(int(j)) == int:
					a = a + str(j) 
				

			except:	
				if type(j) == str:
					if j == ".":
						a = a + str(j)

					else:
						if n == 0 and a != "":
							n1 = float(a)
							dados_x.append(n1)
							n +=1
						elif n == 1 and a != "":
							n2 = float(a)
							dados_y.append(n2)
							n+=1
						a = ""
	return dados_x, dados_y