import cplex
from cplex.exceptions import CplexSolverError
import numpy as np
import utils

DEBUG = True
FILE_NAME = "input/P2_I10_K5_C4.txt"
file_2 = "input/P2_I3_K3_C1.data"

(competitor, theta, permutations) = utils.read_data(file_2)
(I, K) = np.shape(theta)
J = len(permutations[0])


def mip_maximum_capture():
    prob = cplex.Cplex()
    prob.objective.set_sense(prob.objective.sense.maximize)

    c = [1.0 for j in range(J)]

    for c_j in competitor:
        c[int(c_j)] = 2.0
    if DEBUG:
        print(str(c))

    prob.variables.add(obj=[0.0] * J, lb=[0.0] * J, ub=[1.0] * J, types=["I"]*J)
    n_y = I * K * J
    if DEBUG:
        print("Number Variable y(i_k_j) %s" % n_y)
    y_objective_factors = []
    y_variable_name = []
    y_type = ["C" for i in range(n_y)]
    # y_i_k_j
    for i in range(I):
        for k in range(K):
            for j in range(I):
                lambda_i_k = float(theta[i, k])
                factor = lambda_i_k / c[j]
                y_variable_name.append("y_%s_%s_%s" % (i, k, j))
                #y_objective_factors.append(float("{0:.1f}".format(factor)))
                y_objective_factors.append(factor)
    if DEBUG:
        print(y_objective_factors)
        print(y_variable_name)
    prob.variables.add(obj=y_objective_factors, lb=[0.0]*n_y,ub=[cplex.infinity]*n_y, types=y_type,names=y_variable_name)

    prob.write("models/maximum_capture.lp")


mip_maximum_capture()
