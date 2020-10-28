__version__ = '0.1.9'

version = __version__

import sys
from os.path import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from easy_chain.wallet  import Wallet, WalletGanache, BadPassword
from easy_chain.network import Network, network_conf
from easy_chain.tokens  import Tokens

sys.path = bkpath



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
