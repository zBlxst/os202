from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()


if rank == 0:
    token = 1
    comm.send(token, dest=1)
    token = comm.recv(source=size-1)
    print(f"Token : {token}")
elif rank < size - 1:
    token = comm.recv(source=rank-1) + rank + 1
    comm.send(token, dest=rank+1)
else:
    token = comm.recv(source=rank-1) + 1
    comm.send(token, dest=0)    