# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm

from mpi4py import MPI



@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1<<10, 1<<10

scaleX = 3./width
scaleY = 2.25/height
convergence = np.empty((width, height), dtype=np.double)
line_buff = np.empty((width, 1), dtype=np.double)


if rank == 0:
    next_line = 0
    for iProc in range(1,nbp):
        globCom.send(next_line, iProc)
        next_line += 1
        
    stat : MPI.Status = MPI.Status()
    while next_line < height:
        conv = globCom.recv(status=stat) # On reçoit du premier process à envoyer un message
        conv = conv.reshape(conv.shape[0],)
        slaveRk = stat.source
        line = stat.tag
        convergence[:,line] += conv
        globCom.send(next_line, dest=slaveRk)
        next_line += 1
        
    next_line = -1 # next_line vaut maintenant -1 pour signaler aux autres procs qu'il n'y a plus de tâches à exécuter
    for iProc in range(1,nbp):
        stat = MPI.Status()
        conv = globCom.recv(status=stat) # On reçoit du premier process à envoyer un message
        conv = conv.reshape(conv.shape[0],)
        slaveRk = stat.source
        line = stat.tag
        convergence[:,line] += conv
        globCom.send(next_line, dest=slaveRk)
        

else:
    deb = time()
    line = globCom.recv(source=0)
    while line != -1:
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * line)
            line_buff[x] = mandelbrot_set.convergence(c, smooth=True)
        globCom.send(line_buff, dest=0, tag=line)
        line = globCom.recv(source=0)
    fin = time()
    print(f"Temps du calcul pour le rank {rank} de l'ensemble de Mandelbrot : {fin-deb}")

if rank == 0:
    # Constitution de l'image résultante :
    deb = time()
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    fin = time()
    print(f"Temps de constitution de l'image : {fin-deb}")
    image.show()
