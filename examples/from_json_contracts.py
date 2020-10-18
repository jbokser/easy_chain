#!/usr/bin/env python3
import sys, os
from tabulate import tabulate
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from easy_chain.network   import Network
from easy_chain.contracts import ContractsFromJsonFiles

network = Network()

dir_ = "easy_chain/data/contracts"
contracts = ContractsFromJsonFiles(network, dir_ )

table = [ [c.name, len(c.events), len(c.functions), c.address] for c in contracts ]
print()
print(tabulate(table, headers=['Name', 'Events', 'Functions', 'Address']))
print()
