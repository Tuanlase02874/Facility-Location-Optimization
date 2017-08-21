import os
import subprocess
import re
import codecs
import sys
import timeit

if len(sys.argv) == 1:
    input = "location_10_4"
else:
    input = sys.argv[1]

training_folder = os.getcwd() + "/training/%s"%input

# for file_name in os.listdir(training_folder):
#     #print(file_name)
#     file_out_path = "training/%s_model/%s_log"%(input,file_name)
#     os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
#     with open(file_out_path, "w") as file_:
#         subprocess.Popen("./estimate/FL %s/%s"%(training_folder,file_name), stdout=file_, shell=True)

# Read logfile


def process_estimate(training_folder):

    for file_name in os.listdir(training_folder):
        #print(file_name)
        file_out_path = "training/%s_model/%s_log"%(input, file_name)
        os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
        with open(file_out_path, "w") as file_:
            shell_script = "./estimate/FL %s/%s"%(training_folder,file_name)
            print(shell_script)
            p = subprocess.Popen(shell_script, stdout=file_, shell=True)
            p.wait()
            subprocess._cleanup()


def collect_log_estimate(file_log):

    file_out_path = "training/%s_model" % input
    ranks = []
    lamda = []
    with open(file_out_path+ "/%s"%file_log, "rb") as f:
        for line in f:
            l = line.decode("utf-8").strip().replace("\n","")
            if l.find("Ranking collect:") != -1:
                #print(l)
                ranks.append(l.replace("Ranking collect:","").strip())

            if l.find("Lamda:") != -1:
                lamda = [float(theta) for theta in l.replace("Lamda: ","").strip().split()]
    print("Number permutations: %d"%len(ranks))
    #print(len(lamda))
    print("Lamda: %s"%" ".join([str(x) for x in lamda]))
    return ranks, lamda


start = timeit.default_timer()


process_estimate(training_folder)

stop = timeit.default_timer()

print( "Training Time: %d (seconds)"%(stop - start))
#collect_log_estimate("Node_0_log")