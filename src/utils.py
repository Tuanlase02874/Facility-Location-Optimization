import math
# CONF
ALPHA=1
BETA=0.139

def utility_choice(node,customer_i,facility_j):
    return 0.1

def distance_node(node_i, node_j):
    (x_i, y_i) = node_i
    (x_j, y_j) = node_j
    distance = 5.0 + 0.5*math.sqrt((x_i -x_j)**2 + (y_i - y_j)**2)
    return distance


