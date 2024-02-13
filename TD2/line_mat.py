# Produit matrice-vecteur v = A.u
import numpy as np

from mpi4py import MPI

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()



# Dimension du problème (peut-être changé)
dim = 120
# Initialisation de la matrice
part = ((dim*rank) // nbp, (dim*(rank+1)) // nbp)
A = np.array([[(i+j) % dim+1. for i in range(dim)] for j in range(part[0], part[1])])
# print(f"A = {A}")

# Initialisation du vecteur u
u = np.array([i+1. for i in range(dim)])
# print(f"u = {u}")

# Produit matrice-vecteur
v = A.dot(u)
# print(f"v = {v}")

data = np.concatenate(globCom.allgather(v), axis=0)

if rank == 0:
    print(data)
