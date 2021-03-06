#!/usr/bin/env python3
import sys
from os.path import dirname, abspath
sys.path.append(dirname(dirname(abspath(__file__))))

from easy_chain           import Network
from easy_chain.contracts import ContractsFromJsonFiles
from easy_chain.cli       import tabulate

network = Network()

dir_ = "easy_chain/data/contracts/"
contracts = ContractsFromJsonFiles(network, dir_ )

table = [ [c.name, len(c.events), len(c.functions), c.address] for c in contracts ]
print()
print(tabulate(table, headers=['Name', 'Events', 'Functions', 'Address']))
print()
