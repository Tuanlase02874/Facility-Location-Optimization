from random import randint
from random import sample
import matplotlib.pyplot as plt
from collections import Counter

NUMBER_FACILITY_LOCATION = 50            # |I\ = |J|
NUMBER_COMPETITORS_FACILITY_LOCATION = 4 # p
NUMBER_CUSTOMER = 1000
PLAN_SIZE=(100,100)

node = []

file_name = "location_%s_%s"%(NUMBER_FACILITY_LOCATION,NUMBER_COMPETITORS_FACILITY_LOCATION)

def write(node,competitor,customer, fname=file_name):
    index = 0
    fout = open("input/%s.txt"%fname, "w")
    fout.write("Node\t%s\t%s\t%s\n" % ("x", "y","qi"))
    for (x,y) in node:
        index += 1
        fout.write("%s\t%s\t%s\t%s\n"%(index,x,y,customer[index]))
    fout.write("Competitor: \t%s\n"%("\t".join(str(com) for com in competitor)))
    fout.close()

def save_figure(node,fname=file_name):
    fig = plt.figure()
    ax = plt.subplot(111)
    for (x, y) in node:
        ax.plot(x, y, 'ro')
    plt.title("Location Customers and Facilities")
    fig.savefig('graph/%s.png' % fname)

# Random create facility location
(width, height)=PLAN_SIZE
for i in range(NUMBER_FACILITY_LOCATION):
    node.append((randint(0, width), randint(0, height)))

# Random create competitor facility
competitor = []
for i in range(NUMBER_COMPETITORS_FACILITY_LOCATION):
    competitor = sample(range(1, NUMBER_FACILITY_LOCATION), NUMBER_COMPETITORS_FACILITY_LOCATION)

# Random customer
q_i = Counter()
for i in range(NUMBER_CUSTOMER):
    q_i[randint(1,NUMBER_FACILITY_LOCATION)]+=1
#print(sorted(q_i.items()))
#print(q_i[1])
#print(" ".join(competitor))
#print(node)
write(node,competitor,q_i,file_name)
#Plot facility location
save_figure(node,file_name)
#plt.show()




