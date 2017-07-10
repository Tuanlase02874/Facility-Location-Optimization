#!/usr/bin/env python
import os
import matplotlib.pyplot as plt
import numpy as np

log_folder = "training"


def read_file(file_name):
    objective = []
    with open(file_name,"rb") as file_log:
        for line in file_log:
            l = line.decode("utf-8").strip().replace("\n","")
            if l.find("Objective value") != -1:
                objective.append(float(l.split(":")[1]))
    return objective


if __name__ == '__main__':
    file_folder = os.path.join(os.getcwd(),log_folder)
    files = os.listdir(file_folder)
    name_list = []
    objec_list = []
    for f in files:
        name_list.append(f.replace("_0.log", "").replace("_", " "))
        file_name = os.path.join(file_folder, f)
        objective = read_file(file_name)
        objec_list.append(objective)
        print(objective)

    x = np.arange(10)

    fig = plt.figure()
    ax = plt.subplot(111)
    n = len(name_list)
    for i in range(n):
        line, = ax.plot(range(1, len(objec_list[i]) + 1), objec_list[i], label=name_list[i])

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
              ncol=3, fancybox=True, shadow=True)
    plt.xlabel('Iterations')
    plt.ylabel('Objective value')
    plt.show()
