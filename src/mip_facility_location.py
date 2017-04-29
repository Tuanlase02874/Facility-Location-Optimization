import cplex
from cplex.exceptions import CplexSolverError
import numpy as np
import utils

DEBUG = False
CRITICAL_DEBUG = False
FILE_NAME = "input/P2_I10_K5_C4.txt"
FILE_NAME_TEST = "input/P2_I3_K3_C1.data"


def mip_maximum_capture(filename=FILE_NAME):
    (competitor, theta, permutations) = utils.read_data(filename)
    (I, K) = np.shape(theta)
    J = len(permutations[0])
    prob = cplex.Cplex()
    prob.objective.set_sense(prob.objective.sense.maximize)

    c = [1.0 for j in range(J)]

    for c_j in competitor:
        c[int(c_j)] = 2.0
    if DEBUG:
        print(str(c))
    # Add varibales x_j
    prob.variables.add(obj=[0.0] * J, lb=[0.0] * J, ub=[1.0] * J, types=["I"]*J,names=["x_%s"%j for j in range(J)])

    # Add varibales y_i_k_j
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

    # Add Constraints (5)
    for i in range(I):
        for k in range(K):
            ind = []
            for j in range(J):
                ind.append("y_%s_%s_%s" % (i, k, j))
            val = [1.0] * J
            row = [[ind, val]]
            prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[1.0],names=["c%s_%s"%(i,k)])

    # Add constrains (6)
    for i in range(I):
        for k in range(K):
            for j in range(J):
                ind=["y_%s_%s_%s"%(i,k,j),"x_%s"%j]
                val=[1.0,-1.0]
                row = [[ind, val]]
                prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[0.0], names=["d%s_%s_%s" % (i, k, j)])

    # Add constrains (7)
    for i in range(I):
        for k in range(K):
            for j in range(J):
                ts = utils.get_weak_option(permutations[k],j)
                if CRITICAL_DEBUG:
                    print("ts = %s"%list(ts))
                if (len(ts) > 0):
                    ind = []
                    for t in ts:
                        ind.append("y_%s_%s_%s" % (i, k, t))
                    val = [1.0]*len(ts)
                    ind.append("x_%s"%j)
                    val.append(1.0)
                    row = [[ind, val]]
                    prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[1.0], names=["e%s_%s_%s" % (i, k, j)])
    prob.write("models/maximum_capture.lp")

    try:
        prob.solve()
    except CplexSolverError:
        print("Exception raised during solve")
        return

    # Display solution
    print("Solution status = ", prob.solution.get_status())
    for j in range(J):
        print("x_%s : %s"%(j,prob.solution.get_values("x_%s"%j)))

if __name__ == "__main__":
    mip_maximum_capture(FILE_NAME_TEST)
