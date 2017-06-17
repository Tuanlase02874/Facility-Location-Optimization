import sys
import os
import utils
import random
import math


NUMBER_CHOICE=5
NUMBER_ASSORTMENT=3


def read_data(file_name):
    file_input = open('graph/%s'%file_name,"r")
    nodes = []
    for line in file_input:
        l = line.strip().split()
        if l[0].isdigit():
            nodes.append((int(l[1]),int(l[2])))
    return nodes


def utility_choice(node_i,node_j):
    distant_relation = 5.0 + 0.5*utils.distance_node(node_i,node_j)
    u_i_j = utils.ALPHA - utils.BETA*distant_relation + random.random()
    return u_i_j


def utilities(nodes):
    U = []
    for node_i in nodes:
        U_i = []
        for node_j in nodes:
            U_i.append(utility_choice(node_i,node_j))
        U.append(U_i)
    return U


def generate_choice_probabilities(index_i, nodes, number_assortments):
    assorts = []
    pro_assorts = []

    U = utilities(nodes)

    for i in range(number_assortments):
        assort = random.sample(range(0, len(nodes)), 5)
        assorts.append(assort)
        u_assort = [ math.exp(U[index_i][j]) for j in assort]
        sum_pro = sum(u_assort)
        pro_assort = [u_ij/ sum_pro for u_ij in u_assort]
        pro_assort = [float("{0:.2f}".format(pro)) for pro in pro_assort]
        pro_assorts.append(pro_assort)
    return assorts, pro_assorts


if len(sys.argv) == 1:
    input = "location_10_4.txt"
else:
    input = sys.argv[1]

nodes = read_data(input)

index = 0
n_option = len(nodes)

for (x,y) in nodes:
    file_out_path = "training/%s/Node_%s"%(input.replace(".txt",""),index)
    os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
    with open(file_out_path, "w") as f:
        f.write("#Number of options\n")
        f.write("%s\n\n"%n_option)

        f.write("#Assortments data\n")
        assorts, pro_assorts = generate_choice_probabilities(index,nodes,NUMBER_ASSORTMENT)

        for i in range(NUMBER_ASSORTMENT):
            f.write(" ".join([str(ass) for ass in assorts[i]]) + "\n")
            f.write(" ".join([str(pro_ass) for pro_ass in pro_assorts[i]]) + "\n")

    index += 1



