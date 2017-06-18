import os
import subprocess
import re
import codecs


input = "location_10_4"

training_folder =  os.getcwd() + "/training/%s"%input

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
        file_out_path = "training/%s_model/%s_log"%(input,file_name)
        os.makedirs(os.path.dirname(file_out_path), exist_ok=True)
        with open(file_out_path, "w") as file_:
            subprocess.Popen("./estimate/FL %s/%s"%(training_folder,file_name), stdout=file_, shell=True)

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
    return ranks,lamda

#process_estimate(training_folder)
collect_log_estimate("Node_0_log")