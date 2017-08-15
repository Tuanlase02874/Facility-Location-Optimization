#!/usr/bin/env python
import os
import matplotlib.pyplot as plt
import numpy as np

if __name__ == '__main__':
    nodes_k20 = [13, 243, 2118, 21128, 75714]
    nodes_k30 = [26, 740, 5028, 46161, 139320]
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
    plt.ylabel('Training running time (s)')
    plt.show()