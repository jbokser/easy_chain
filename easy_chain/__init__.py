import sys
from os.path import dirname, abspath

base_dir = dirname(abspath(__file__))

with open(base_dir + "/version.txt", "r") as file_:
    version = file_.read().split()[0]
__version__ = version

bkpath   = sys.path[:]
sys.path.append(dirname(base_dir))

from easy_chain.wallet  import Wallet, WalletGanache, BadPassword
from easy_chain.network import Network, network_conf
from easy_chain.tokens  import Tokens

sys.path = bkpath



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print('Version: {}'.format(version))
