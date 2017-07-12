#!/usr/bin/env python
import os
import matplotlib.pyplot as plt
import numpy as np

file_name="result.dat"

def read_file(file_result=file_name):
    nodes_k20 = []
    nodes_k30 = []
    with open(file_name,"r") as result:
        for line in result:
            #print(line.strip().replace("\\", ""))
            data = line.strip().replace("\\", "").split("&")
            if int(data[1].strip())==20:
                nodes_k20.append(float(data[5].strip()))

            if int(data[1].strip())==30:
                nodes_k30.append(float(data[5].strip()))
    return nodes_k20, nodes_k30
if __name__ == '__main__':
    nodes_k20, nodes_k30 = read_file()
    print(nodes_k20)
    print(nodes_k30)

    fig = plt.figure()
    ax = plt.subplot(111)
    n = len(nodes_k20)

    line, = ax.plot(range(10, 60 ,10), nodes_k20, label="K = 20")
    line, = ax.plot(range(10, 60 ,10), nodes_k30, label="K = 30")

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),
              ncol=3, fancybox=True, shadow=True)
    plt.xlabel('Number of instances (node)')
    plt.ylabel('Optimization running time (s)')
    plt.show()