# Calcul pi par une méthode stochastique (convergence très lente !)
import time
import numpy as np

from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# Nombre d'échantillons :
nb_samples = 40_000_000

if rank == 0:
    values = np.array([0]*(size-1), dtype=float)
    beg = time.time()
    for i in range(size-1):
        values[i] = comm.recv()
    approx_pi = values.mean()
    end = time.time()

    print(f"Temps pour calculer pi : {end - beg} secondes")
    print(f"Pi vaut environ {approx_pi}")
    
else:
    # Nombre d'échantillons :
    nb_samples_proc = nb_samples // (size - 1)
    # Tirage des points (x,y) tirés dans un carré [-1;1] x [-1; 1]
    x = 2.*np.random.random_sample((nb_samples_proc,))-1.
    y = 2.*np.random.random_sample((nb_samples_proc,))-1.
    # Création masque pour les points dans le cercle unité
    filtre = np.array(x*x + y*y < 1.)
    # Compte le nombre de points dans le cercle unité
    sum = np.add.reduce(filtre, 0)
    approx_pi = 4.*sum/nb_samples_proc
    
    comm.send(approx_pi, dest=0)



