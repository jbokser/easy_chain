import sys, json
from sys      import path
from os       import listdir
from tabulate import tabulate
from os.path  import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.append(dirname(base_dir))

from easy_chain.conf      import get as config
from easy_chain.contracts import ERC20

sys.path = bkpath



def config_call_back(options):
    return {
        'tokens_conf': options 
    }

config(locals(),
       config_call_back,
       ['tokens.json', 'tokens_default.json'],
       'tokens',
       env_pre = 'wallet')



class Token(ERC20):
    pass



class Tokens(list):

    def __init__(self, network):
        self._network = network
        self.profile = network.profile
        token_dict = tokens_conf.get(self.profile, {})
        for key, value in token_dict.items():
            self.append(Token(network, key, **value))
        
    def __call__(self, search):
        for token in self:
            if str(search).lower() in [token.address.lower(),
                                       token.name.lower(),
                                       token.symbol.lower()]:
                return token
        return None



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    from network import Network, network_conf
    table = []
    for profile in network_conf.network_profiles.keys():
        network = Network(profile)
        tokens = Tokens(network)
        for t in tokens:
            table.append(t.as_dict)
    print()
    print(tabulate(table, headers={}))
    print()
