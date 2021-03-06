import json
from os.path import dirname, abspath
from web3    import Web3 


work_dir = dirname(dirname(abspath(__file__)))



class ContractBase(object):


    def __init__(self, network, abi,
        address  = None,
        name     = None,
        bytecode = None,
        warning  = lambda x: None):

        self.warning = warning

        if address:
            address = network.Address(address)
        else:
            address = None

        self.name = name

        self._network = network
        self._address = address
        self._abi     = abi
        self._bytecode = bytecode

        self._load()


    def _load(self):
        try:
            self._contract = self._network.web3.eth.contract(
                address  = self._address,
                abi      = self._abi,
                bytecode = self._bytecode)
        except self._network.InvalidAddress as e:
            try:
                message, addr = e.args
                self.warning(f'{addr} {message}')
            except:
                self.warning(str(e))

            self._contract = self._network.web3.eth.contract(
                address  = Web3.toChecksumAddress(self._address.lower()),
                abi      = self._abi,
                bytecode = self._bytecode)




    def __bool__(self):
        return (bool(self._address))


    @property
    def network(self):
        return self._network


    @network.setter
    def network(self, value):
        self._network = value
        self._load()


    @property
    def address(self):
        return self._address


    @address.setter
    def address(self, value):
        self._address = self._network.Address(value)
        self._load()


    @property
    def abi(self):
        return self._abi


    @abi.setter
    def abi(self, value):
        self._abi = value
        self._load()


    @property
    def bytecode(self):
        return self._bytecode


    @bytecode.setter
    def bytecode(self, value):
        self._bytecode = value
        self._load()


    @property
    def profile(self):
        return self._network.profile


    @property
    def functions(self):
        return [ fnc_name for fnc_name in self._contract.functions]
    

    @property
    def owner(self):
        if not 'owner' in self.functions:
            return None
        return self.function_call('owner')


    @property
    def events(self):
        return [ e.__name__ for e in self._contract.events ]


    def get_events_args(self, event_name, transaction):
        receipt = self._network.get_transaction_receipt(transaction)
        events = []
        if receipt and 'blockNumber' in receipt:
            events = [ e for e in self.get_events(
                events_names = [event_name],
                from_block   = receipt['blockNumber'],
                to_block     = receipt['blockNumber'],
                step         = 1) if e["transactionHash"]==transaction]
        return [ e['args'] for e in events ]


    def get_events(self,
                   events_names = [],
                   from_block   = 0,
                   to_block     = 'latest',
                   step         = 100,
                   reverse = False):
        
        if not events_names:
            events_names = self.events

        if to_block  == 'latest':
            to_block  = self._network.block_number

        if not from_block:
            from_block = self._network.block_number -100       

        def normalize(value):
            if 'items' in dir(value):
                value = dict(value.items())
                for key in list(value.keys()):
                    value[key] = normalize(value[key])
            if 'hex' in dir(value):
                value = value.hex()
            return value        

        def make_chunks(from_, to_, step_, reverse):
            from_ , to_, step_ = int(from_) , int(to_), int(step_)  
            if from_ <0:
                from_ = 0
            if to_ <0:
                to_ = 0
            if from_ == to_:
                yield dict(fromBlock=from_, toBlock=to_)
            else:
                if from_ > to_:
                    prev_from = from_
                    from_     = to_
                    to_       = prev_from
                if step_ < 1:
                    step_ = 1
                if reverse:
                    i = to_
                    while i > from_:
                        chunk_from = i - step_ + 1
                        if chunk_from < from_:
                            chunk_from = from_
                        yield dict(fromBlock=chunk_from, toBlock=i)
                        i -= step_
                    if chunk_from > from_:
                        yield dict(fromBlock=from_, toBlock=chunk_from-1)
                else:
                    i = from_
                    while i < to_:
                        chunk_to = i + step_ - 1
                        if chunk_to > to_:
                            chunk_to = to_
                        yield dict(fromBlock=i, toBlock=chunk_to)
                        i += step_
                    if chunk_to < to_:
                        yield dict(fromBlock=chunk_to, toBlock=to_)

        for kargs in make_chunks(from_block, to_block, step, reverse):
            chunk = []
            for events in self._contract.events:
                if events.__name__ in events_names:
                    for event in events.createFilter(**kargs).get_all_entries():
                        event = normalize(event)
                        chunk.append(event)
            chunk.sort(key = lambda x: x["blockNumber"], reverse=reverse)
            for e in chunk:
                yield e


    def get_last_events(self, events_names = [], top_=10):
        to_block  = self._network.block_number
        from_block = to_block - 100
        i = 0
        while True:
            kargs = dict(events_names = events_names,
                         from_block   = from_block,
                         to_block     = to_block,
                         reverse      = True)
            for event in self.get_events(**kargs):
                yield event
                i += 1
                if i >= top_:
                    break
            if i >= top_:
                break
            to_block = from_block - 1
            from_block = to_block - 100


    def _function(self, fnc_name, *args):
        if not fnc_name in self.functions:
            raise ValueError("Function {} not found.".format(repr(fnc_name)))
        fnc = getattr(self._contract.functions, fnc_name)
        return fnc(*args)


    def function_call(self, fnc_name, *args, **kargs):
        block_identifier = None
        if kargs:
            for k in ['block_identifier', 'block_number', 'block']:
                if k in kargs:
                    v = kargs[k]
                    del kargs[k]
                    if v:
                        block_identifier = v
            if 'from' in kargs:
                kargs['from'] = self._network.Address(kargs['from'])
            if block_identifier:
                return self._function(fnc_name, *args).call(kargs, block_identifier=block_identifier)
            else:
                return self._function(fnc_name, *args).call(kargs)
        else:
            return self._function(fnc_name, *args).call()


    def function_call_from_address_1(self, fnc_name, *args, **kargs):
        kargs['from'] = 1
        return self.function_call(fnc_name, *args, **kargs)


    def transaction_data(self,
                 fnc_name,
                 *args):

        contract_function = self._function(fnc_name, *args)
        return contract_function.buildTransaction()['data']



    def transaction(self,
                 sign_callback,
                 from_address,
                 fnc_name,
                 *args,
                 gas_limit = 0,
                 gas_price = 'auto'):

        from_address      = self._network.Address(from_address)
        contract_function = self._function(fnc_name, *args)

        return self._network.transaction(
            sign_callback     = sign_callback,
            contract_function = contract_function,
            from_address      = from_address,
            gas_limit         = gas_limit,
            gas_price         = gas_price )


    def deploy(self,
               sign_callback,
               from_address,
               *args,
               gas_limit = 0,
               gas_price = 'auto'):

        from_address      = self._network.Address(from_address)
        contract_function = self._contract.constructor(*args)

        return self._network.transaction(
            sign_callback     = sign_callback,
            contract_function = contract_function,
            from_address      = from_address,
            gas_limit         = gas_limit,
            gas_price         = gas_price )


    def dict_constructor(self, properties=[]):
        out = {}
        for attr_name in dir(self):
            if attr_name[0]!='_' and attr_name not in [
                    'as_dict', 'json', 'owner', 'network']:
                attr = getattr(self, attr_name)
                if not '__call__' in dir(attr):
                    if not(properties) or (attr_name in properties):
                        out[attr_name] = attr
        return out


    @property
    def as_dict(self):
        return self.dict_constructor()


    @property
    def json(self):
        out = {'abi': self.abi}
        if self.bytecode:
            out['bytecode'] = self.bytecode
        if self.name:
            out['contractName'] = self.name
        return json.dumps(out, indent=4, sort_keys=True)


    def __str__(self):
        if self.name and self.address:
            return "Contarct {} {}".format(
                self.name,
                self.address)
        else:
            s = "Contarct {}"
            if self.name:         
                return s.format(self.name)
            if self.address:         
                return s.format(self.address)
        return repr(self)


    def __repr__(self):
        return object.__repr__(self)


class Contract(ContractBase):

    def __init__(self, network,
                 address       = None,
                 abi           = None,
                 name          = None,
                 bytecode      = None,
                 json_path     = None,
                 json_file     = None,
                 abi_path      = None,
                 abi_file      = None,
                 bytecode_path = None,
                 bytecode_file = None,
                 warning       = lambda x: None):

        if not name and json_path and json_file:
            json_full_path = json_path + '/' + json_file
            json_full_path = json_full_path.format(
                work_dir = work_dir,
                profile  = network.profile,
                uuid     = network.uuid)
            try:
                with open(json_full_path, 'r') as file_:
                    data = json.load(file_)
            except:
                data = None
            if isinstance(data, dict) and 'contractName' in data:
                name = data['contractName']

        if not abi:
            if json_path and not abi_path:
                abi_path = json_path
            if json_file and not abi_file:
                abi_file = json_file
            if abi_path and abi_file:
                abi_full_path = abi_path + '/' + abi_file
                abi_full_path = abi_full_path.format(
                    work_dir = work_dir,
                    profile  = network.profile,
                    uuid     = network.uuid,
                    name     = '{name}')
                if name:
                    abi_full_path = abi_full_path.format(
                        name = name)
                if not '{name}' in abi_full_path:
                    try:
                        with open(abi_full_path, 'r') as file_:
                            data = json.load(file_)
                    except:
                        data = None
                    if isinstance(data, dict) and 'abi' in data:
                        abi = data['abi']
                    if isinstance(data, list):
                        abi = data

        if not bytecode:
            if json_path and not bytecode_path:
                bytecode_path = json_path
            if json_file and not bytecode_file:
                bytecode_file = json_file
            if bytecode_path and bytecode_file:
                bytecode_full_path = bytecode_path + '/' + bytecode_file
                bytecode_full_path = bytecode_full_path.format(
                    work_dir = work_dir,
                    profile  = network.profile,
                    uuid     = network.uuid,
                    name     = '{name}')
                if name:
                    bytecode_full_path = bytecode_full_path.format(
                        name = name)
                if not '{name}' in abi_full_path:
                    try:
                        with open(bytecode_full_path, 'r') as file_:
                            data = json.load(file_)
                    except:
                        try:
                            with open(bytecode_full_path, 'r') as file_:
                                data = file_.read()
                        except:
                            data = None
                    if data:
                        if isinstance(data, dict):
                            if 'bytecode' in data:
                                bytecode = data['bytecode']
                        else:
                            bytecode = data

        if not abi:
            raise ValueError('No ABI')

        ContractBase.__init__(self,
            network  = network,
            abi      = abi,
            address  = address,
            name     = name,
            bytecode = bytecode,
            warning  = warning)



if __name__ == '__main__':

    print("File: {}, Ok!".format(repr(__file__)))

    import sys, os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from network import Network

    network = Network('rsk_testnet')

    kargs = {
        "network":  network,
        "address":  "0xCb46C0DdC60d18eFEB0e586c17AF6Ea36452DaE0",
        "name":     "TokenDollarOnChain",
        "abi_path": "{work_dir}/data/contracts",
        "abi_file": "erc20.json"}

    contract = Contract(warning = lambda x: print(f'WARNING: {x}'), **kargs)
    contract.dict_constructor()
    