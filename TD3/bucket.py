from mpi4py import MPI

from random import random

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

dim = 120

if rank == 0:
    li = [random() for _ in range(dim)]
    for i in range(1, nbp):
        globCom.send(list(filter(lambda x : (i / nbp) < x <= ((i+1)/nbp), li)), dest=i)
    to_sort = list(filter(lambda x : x <= (rank+1)/nbp, li))
else:
    to_sort = globCom.recv(source=0)


sorted_list = sorted(to_sort)

final = sum(globCom.allgather(sorted_list), [])

if rank == 0:
    print(final)