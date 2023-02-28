import os
from ctypes import CDLL, c_int, POINTER


# Define the Igraph interface
class Igraph:
    def fast_greedy(self, edges, res, lenn):
        pass


# Load the GraphMod library and define its functions
if os.name == 'nt':  # Windows
    libgraph = CDLL('GraphMod.dll')
elif os.name == 'posix':  # Linux, macOS
    libgraph = CDLL('libGraphMod.so')
else:
    raise OSError('Unsupported operating system')
libgraph.fastGreedy.argtypes = [POINTER(c_int), POINTER(c_int), c_int]
libgraph.fastGreedy.restype = None


# Define the MakeClusters class
class MakeClusters:
    def get_fast_greedy_res(self, edges, reslen):
        # Set the library path and load the Igraph interface
        os.environ['PATH'] = os.environ.get('PATH', '') + os.pathsep + os.path.abspath('libgraph')
        igraph = Igraph()

        # Call the fastGreedy function and return the result
        res = (c_int * reslen)()
        igraph.fast_greedy(edges, res, len(edges))
        return res
