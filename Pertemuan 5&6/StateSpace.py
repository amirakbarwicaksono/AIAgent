import networkx as nx
import matplotlib.pyplot as plt

# Grid 3x3, setiap posisi adalah state (x,y)
states = [(x,y) for x in range(3) for y in range(3)]

# Buat graph state space
G = nx.Graph()
for x,y in states:
    for dx,dy in [(0,1),(1,0),(0,-1),(-1,0)]: # gerakan 4 arah
        nx_, ny_ = x+dx, y+dy
        if 0 <= nx_ < 3 and 0 <= ny_ < 3:
            G.add_edge((x,y),(nx_,ny_))

# Plot state space
pos = {state: (state[1], -state[0]) for state in states}  # layout grid
nx.draw(G, pos, with_labels=True, node_size=600, node_color="lightblue")
plt.title("State Space untuk Grid 3x3")
plt.show()


#Contoh agar case yang dipelajari lebih mudah dimengerti.