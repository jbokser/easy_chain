__version__ = '0.1.5'

import sys
from os.path import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(base_dir)

from wallet  import Wallet, WalletGanache, BadPassword
from network import Network, network_conf
from tokens  import Tokens

sys.path = bkpath



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
