#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain import WalletGanache, Wallet, Network

network = Network('ganache')

# Non persistent wallet with the deterministic Gananche address
wallet_ganache = WalletGanache()
wallet         = Wallet(network.uuid)

for key, value in wallet_ganache.items():
    name = wallet_ganache.get_name(key)
    print('{}: {}'.format(name, key))
    wallet.add_priv_key(value, encrypt=False, name=name)
