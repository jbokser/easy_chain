#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.wallet    import Wallet
from easy_chain.network   import Network
from easy_chain.contracts import ERC20

network = Network('rsk_testnet')
wallet  = Wallet(network.uuid)
token   = ERC20(network, "0xCb46C0DdC60d18eFEB0e586c17AF6Ea36452DaE0")

print()
print(token.name)
for address in wallet:
    print('{} = {} {}'.format(
        address,
        token.balance(address),
        token.symbol))
print()
