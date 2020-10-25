#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain.network   import Network
from easy_chain.contracts import ERC20

network = Network()

token = ERC20(network, name='ERC20')

print(token.json)