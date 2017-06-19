import cplex
from cplex.exceptions import CplexSolverError
import numpy as np
import utils
import csv
import os
import pprint

DEBUG = False
CRITICAL_DEBUG = False
FILE_NAME = "input/P2_I10_K5_C4.data"
FILE_NAME_TEST = "input/P2_I3_K3_C1.data"
FILE_NAME_TEST2 = "input/P2_I10_K3_C3.data"
FILE_RESULTS="mip_results.csv"

input_mode="location_10_4_model"

def collect_log_estimate(file_log):
    ranks = []
    lamda = []
    with open(file_log, "rb") as f:
        for line in f:
            l = line.decode("utf-8").strip().replace("\n","")
            if l.find("Ranking collect:") != -1:
                #print(l)
                rank_string = l.replace("Ranking collect:","").strip()
                ranks.append([int(x) for x in rank_string.split()])
            if l.find("Lamda:") != -1:
                lamda = [float(theta) for theta in l.replace("Lamda: ","").strip().split()]
    if DEBUG:
        print("Number permutations: %d"%len(ranks))
        print("Ranks[1][2] %d"%ranks[1][2])
        print("Lamda: %s"%" ".join([str(x) for x in lamda]))
    return ranks,lamda

def read_data_q_competitor(name_model=input):
    q = []
    competitor = []
    with open("graph/%s"%name_model.replace("_model",".txt"),"r") as f:
        for line in f:
            l_data = line.strip().split()
            #print(l_data)
            if l_data[0].isdigit():
                q.append(int(l_data[3]))
            if l_data[0] == "Competitor:":
                competitor = [int(com) for com in l_data[1:]]
    if DEBUG:
        print(competitor)
        print(q)
    return q, competitor


def read_data_permutation(name_model=input_mode):

    log_path = os.getcwd()+"/training/%s"%input_mode
    files_list_log = os.listdir(log_path)
    lamda_customer_zones = []
    ranks_customer_zones = []
    for file_name_log in files_list_log:
        ranks, lamda = collect_log_estimate(log_path+"/"+file_name_log)
        lamda_customer_zones.append(lamda)
        ranks_customer_zones.append(ranks)
    return lamda_customer_zones, ranks_customer_zones

def mip_maximum_capture(input_mode=input_mode,r=1):

    #(competitor, theta, permutations,q) = utils.read_data(filename)
    q,competitor = read_data_q_competitor(input_mode)
    lamda_customer_zones, ranks_customer_zones = read_data_permutation(input_mode)

    I = len(q)
    J = I

    # Load permutations an lamda

    prob = cplex.Cplex()
    start_time = prob.get_time()
    prob.objective.set_sense(prob.objective.sense.maximize)

    c = [1.0 for j in range(J)]

    for c_j in competitor:
        c[int(c_j)] = 2.0
    if DEBUG:
        print(str(c))
    # Add variables x_j
    prob.variables.add(obj=[0.0] * J, lb=[0.0] * J, ub=[1.0] * J, types=["I"]*J,names=["x_%s"%j for j in range(J)])

    # Add variables y_i_k_j
    index_variable_y = 0
    y_objective_factors = []
    y_variable_name = []

    # y_i_k_j
    for i in range(I):
        K = len(lamda_customer_zones[i])
        for j in range(J):
            for k in range(K):
                lambda_i_k = lamda_customer_zones[i][k]
                factor = q[i]*lambda_i_k / c[j]
                y_variable_name.append("y_%s_%s_%s" % (i, k, j))
                #y_objective_factors.append(float("{0:.1f}".format(factor)))
                y_objective_factors.append(factor)
    if DEBUG:
        print(y_objective_factors)
        print(y_variable_name)
    n_y = len(y_variable_name)
    y_type = ["C" for i in range(n_y)]
    prob.variables.add(obj=y_objective_factors, lb=[0.0]*n_y,ub=[cplex.infinity]*n_y, types=y_type,names=y_variable_name)

    # Add Constraints (5)
    for i in range(I):
        K = len(lamda_customer_zones[i])
        for k in range(K):
            ind = []
            for j in range(J):
                ind.append("y_%s_%s_%s" % (i, k, j))
            val = [1.0] * J
            row = [[ind, val]]
            prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[1.0],names=["c%s_%s"%(i,k)])

    # Add constraints (6)
    for i in range(I):
        K = len(lamda_customer_zones[i])
        for k in range(K):
            for j in range(J):
                ind=["y_%s_%s_%s"%(i,k,j),"x_%s"%j]
                val=[1.0,-1.0]
                row = [[ind, val]]
                prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[0.0], names=["d%s_%s_%s" % (i, k, j)])

    # Add constraints (7)
    for i in range(I):
        K = len(lamda_customer_zones[i])
        for k in range(K):
            for j in range(J):
                ts = utils.get_weak_option(ranks_customer_zones[i][k],j)
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

    # for j in range(J):
    #     ind = []
    #     for i in range(I):
    #         for k in range(K):
    #             ts = utils.get_weak_option(permutations[k], j)
    #             if CRITICAL_DEBUG:
    #                 print("ts = %s" % list(ts))
    #             if (len(ts) > 0):
    #                 for t in ts:
    #                     ind.append("y_%s_%s_%s" % (i, k, t))
    #     ind.append("x_%s" % j)
    #     val = [1.0]*len(ind)
    #     row = [[ind, val]]
    #     prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[1.0])

    # Add constraints (8)
    for i in range(I):
        K = len(lamda_customer_zones[i])
        for k in range(K):
            for c_j in competitor:
                ts = utils.get_weak_option(ranks_customer_zones[i][k],int(c_j))
                if CRITICAL_DEBUG:
                    print("ts = %s"%list(ts))
                if (len(ts) > 0):
                    ind = []
                    for t in ts:
                        ind.append("y_%s_%s_%s" % (i, k, t))
                    val = [1.0]*len(ts)
                    row = [[ind, val]]
                    prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[0.0], names=["e%s_%s_%s" % (i, k, j)])

    # for c_j in competitor:
    #     ind = []
    #     for i in range(I):
    #         for k in range(K):
    #             ts = utils.get_weak_option(permutations[k], int(c_j))
    #             if CRITICAL_DEBUG:
    #                 print("ts = %s" % list(ts))
    #             if (len(ts) > 0):
    #                 for t in ts:
    #                     ind.append("y_%s_%s_%s" % (i, k, t))
    #     val = [1.0]*len(ind)
    #     row = [[ind, val]]
    #     prob.linear_constraints.add(lin_expr=row, senses="L", rhs=[0.0])




    # Add constraint (9)
    ind =[]
    for j in range(J):
        ind.append("x_%s" % j)
    val = [1.0] * J
    row = [[ind, val]]
    print(r)
    prob.linear_constraints.add(lin_expr=row, senses="E", rhs=[r])

    prob.write("models/maximum_capture.lp")
    #start_time = prob.get_time()
    try:

        prob.solve()
    except CplexSolverError:
        print("Exception raised during solve")
        return
    end_time = prob.get_time()
    # Display solution
    print("Solution status = ", prob.solution.get_status())
    print("Solution value  = ", prob.solution.get_objective_value())
    for j in range(J):
        print("x_%s : %s"%(j,prob.solution.get_values("x_%s"%j)))

    # #print result y
    # for i in range(I):
    #     for k in range(K):
    #         for j in range(I):
    #             lambda_i_k = float(theta[i, k])
    #             factor = lambda_i_k / c[j]
    #             y_variable_name.append("y_%s_%s_%s" % (i, k, j))
    #             variable_name = "y_%s_%s_%s" % (i, k, j)
    #             print("Result %s :"%variable_name,prob.solution.get_values(variable_name))


    # #Write result to file
    header = ["I", "J", "Number Competitors", "r (Number new facilities)", "Number Variables(x,y)",
              "Number Constraints", "Objective Value", "Times (sec)"]
    try:
        csvfile = open('results/%s' % FILE_RESULTS, 'r')
        print("Loaded Result File")
    except FileNotFoundError:
        print("Create new Result File")
        with open('results/%s' % FILE_RESULTS, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(header)
    result = [I, J, len(competitor),r,prob.variables.get_num(),
              prob.linear_constraints.get_num(), "%.2f" % prob.solution.get_objective_value(), "%.4f"%(end_time-start_time)]
    with open('results/%s' % FILE_RESULTS, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(result)

if __name__ == "__main__":
    # mip_maximum_capture(FILE_NAME_TEST,1)
    #file_names= sorted(os.listdir(os.getcwd()+"/input"))
    #print(file_name[1])
    # for i in range(1,11):
    #     mip_maximum_capture("input/P2_I10_K30_C5.data", i)
    #read_data_q_competitor()

    #mip_maximum_capture("input/P2_I50_K50_C5.data", 5)
    # for file_name in file_names:
    #     for i in [1,2,4,6,8]:
    #         mip_maximum_capture("input/%s"%file_name,i)
    #mip_maximum_capture(FILE_NAME_TEST, 3)
    #read_data_permutation(input_mode)
    mip_maximum_capture(input_mode,4)