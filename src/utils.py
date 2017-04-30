import math
import pprint
import numpy as np

# CONF
ALPHA=1
BETA=0.139
FILE_NAME = "input/P2_I10_K5_C4.txt"


def utility_choice(node,customer_i,facility_j):
    return 0.1


def distance_node(node_i, node_j):
    (x_i, y_i) = node_i
    (x_j, y_j) = node_j
    distance = 5.0 + 0.5*math.sqrt((x_i -x_j)**2 + (y_i - y_j)**2)
    return distance


def read_data(fname=FILE_NAME,debug=False):

    theta=[]
    permutations=[]

    fdata = open(fname,'r')

    (NUMBER_COMPETITOR, I, J, K) = [int(a) for a in fdata.readline().strip().split("\t")[1].replace("(","").replace(")","").split(',')]
    if debug:
        print("(NUMBER_COMPETITOR, I, J, K) = %s " % str((NUMBER_COMPETITOR, I, J, K)))

    competitor = fdata.readline().strip().split("\t")[1:]
    if debug:
        print("Competitors: %s"%str(competitor))

    for k in range(K):
        permutation = fdata.readline().strip().split("\t")[1:]
        permutation_int = [int(i) for i in permutation]
        permutations.append(permutation_int)
    if debug:
        print("%s Permutations: "%K)
        pprint.pprint(permutations)

    for i in range(I):
        theta_i = fdata.readline().strip().split("\t")[1:]
        theta.append(theta_i)
    if debug:
        print("Lambda size [%s,%s]"%np.shape(np.array(theta)))

    # Read q
    q_str = fdata.readline().strip().split("\t")[1:]
    q = [int(q_i) for q_i in q_str]
    if debug:
        print("q %s"% q)

    return (competitor,np.array(theta),permutations,q)


def get_weak_option(permutation_k,option_j=1):
    index = permutation_k.index(option_j)
    return permutation_k[index+1:]

#(competitor,theta,permutations) = read_data()

