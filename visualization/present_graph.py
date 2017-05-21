#!/usr/bin/env python
"""
Draw a graph with matplotlib.
You must have matplotlib for this to work.
"""
import matplotlib.pyplot as plt
import networkx as nx

G=nx.complete_graph(70)
nx.draw(G)
plt.savefig("../graph/simple_path.png") # save as png
plt.show() # display