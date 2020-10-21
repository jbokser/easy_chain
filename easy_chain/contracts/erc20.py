from base import Contract



class ERC20(Contract):

    def __init__(self, network,
                 address  = None,
                 symbol   = None,
                 decimals = 0,
                 name=None):

        self.symbol    = symbol
        self.decimals  = decimals

        Contract.__init__(self, network,
                          address       = address,
                          name          = name,
                          json_path     = '{work_dir}/data/contracts',
                          json_file     = 'erc20.json')


    def _load(self):

        Contract._load(self)

        for attr in ['name', 'symbol', 'decimals']:
            if not getattr(self, attr):
                try:
                    obtained = self.function_call(attr)
                except:
                    obtained = None
                if obtained:
                    setattr(self, attr, obtained)

        if self.symbol and not self.name:
            self.name = self.symbol

        if self.name and not self.symbol:
            self.symbol = self.name


    @property
    def as_dict(self):
        return self.dict_constructor([
            'name',
            'symbol',
            'address',
            'profile',
            'decimals'])


    def __str__(self):
        if self.name and self.symbol and (self.name != self.symbol):
            return 'Token {} ({})'.format(
                self.name,
                self.symbol)
        s = 'Token {}'
        if self.name:
            return s.format(self.name)
        if self.symbol:
            return s.format(self.symbol)
        if self.address:
            return s.format(self.address)
        return repr(self)


    def __repr__(self):
        return object.__repr__(self)


    def deploy(self,
               sign_callback,
               from_address,
               gas_limit = 0,
               gas_price = 0):

        name   = self.name
        symbol = self.symbol

        if not name:
            name = ''

        if not symbol:
            symbol = ''

        return Contract.deploy(self,
                               sign_callback,
                               from_address,
                               name,
                               symbol,
                               gas_limit = gas_limit,
                               gas_price = gas_price) 


    def balance(self, address):
        address = self._network.Address(address)
        value = self.function_call('balanceOf', address)
        if self.decimals:
            value = value / (10 ** self.decimals)
        return value


    def transfer(self,
                 sign_callback,
                 from_address,
                 to_address,
                 value,
                 gas_limit = 0,
                 gas_price = 0):

        from_address = self._network.Address(from_address)
        to_address   = self._network.Address(to_address)
        value        = int(value * (10 ** self.decimals))

        return self.transaction(
            sign_callback,
            from_address,
            'transfer',
            to_address,
            value,
            gas_limit = gas_limit,
            gas_price = gas_price)



    def mint(self,
             sign_callback,
             from_address,
             to_address,
             value,
             gas_limit = 0,
             gas_price = 0):

        from_address = self._network.Address(from_address)
        to_address   = self._network.Address(to_address)
        value        = int(value * (10 ** self.decimals))

        return self.transaction(
            sign_callback,
            from_address,
            'mint',
            to_address,
            value,
            gas_limit = gas_limit,
            gas_price = gas_price)


    def burn(self,
             sign_callback,
             from_address,
             to_address,
             value,
             gas_limit = 0,
             gas_price = 0):

        from_address = self._network.Address(from_address)
        to_address   = self._network.Address(to_address)
        value        = int(value * (10 ** self.decimals))

        return self.transaction(
            sign_callback,
            from_address,
            'burn',
            to_address,
            value,
            gas_limit = gas_limit,
            gas_price = gas_price)



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
