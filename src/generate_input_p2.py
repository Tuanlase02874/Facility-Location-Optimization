from random import randint
from random import sample
import numpy as np
import random

NUMBER_COMPETITOR = 10
I = 30
J = 10
K = 3
FILE_NAME = "P2_I%s_K%s_C%s"%(I,K,NUMBER_COMPETITOR)


# Random competitors
competitor = sample(range(0,J),NUMBER_COMPETITOR)
print(competitor)

# Random lambda
theta = []

# Random q_i
q = [randint(1,9)*1000  for i in range(I)]

for i in range (I):
    theta_i = [randint(2,8)  for i in range(K)]
    theta_i_nm = [i/sum(theta_i) for i in theta_i]
    theta.append(theta_i_nm)

print("I=%s K=%s"%np.shape(np.array(theta)))


def write(competitor, theta,q, fname=FILE_NAME):
    fout = open("input/%s.data"%fname, "w")
    fout.write("(NUMBER_COMPETITOR,I,J,K)\t(%s,%s,%s,%s)\n"%(NUMBER_COMPETITOR,I,J,K))
    fout.write("COMPETITORS\t%s\n" % "\t".join([str(i) for i in competitor]))
    #fout.write("%s Permutations:\n"%K)
    for k in range(K):
        facilities = [j for j in range(0,J)]
        random.shuffle(facilities)
        print(facilities)
        fout.write("k=%s:\t%s\n"%(k,"\t".join([str(rank) for rank in facilities])))

    #Write theta
    for i in range(I):
        fout.write("Lambda_%s:\t%s\n" % (i, "\t".join([str(la) for la in theta[i]])))

    # Write p_i
    fout.write("q:\t%s\n" % ("\t".join([str(q_i) for q_i in q])))

    fout.close()

write(competitor,theta,q, FILE_NAME)

