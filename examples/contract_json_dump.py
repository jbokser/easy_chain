#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.network   import Network
from easy_chain.contracts import ERC20

network = Network()

token = ERC20(network, name='ERC20')

print(token.json)