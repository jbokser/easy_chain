from base import Contract



class MultiSigWallet(Contract):

    def __init__(self, network,
                 address = None,
                 name    = None):
        Contract.__init__(self, network,
                          address       = address,
                          name          = name,
                          abi_path      = '{work_dir}/data/contracts',
                          abi_file      = 'multisig.json',
                          bytecode_path = '{work_dir}/data/contracts',
                          bytecode_file = 'multisig.json')


    def __str__(self):
        if self.name and self.address:
            return 'MultiSigWallet {} ({})'.format(
                self.name,
                self.address)
        s = 'MultiSigWallet {}'
        if self.name:
            return s.format(self.name)
        if self.address:
            return s.format(self.address)
        return repr(self)


    def __repr__(self):
        return object.__repr__(self)

    def deploy(self,
               sign_callback,
               from_address,
               accounts,
               required_confirmations,
               gas_limit = 0,
               gas_price = 0):


        Address = self._network.Address

        accounts = [ Address(a) for a in accounts]
        required_confirmations = int(required_confirmations)
        if required_confirmations < 1:
            required_confirmations = 1

        return Contract.deploy(self,
                               sign_callback,
                               from_address,
                               accounts,
                               required_confirmations,
                               gas_limit = gas_limit,
                               gas_price = gas_price) 

    @property
    def owners(self):
        return self.function_call('getOwners')

    @property
    def transaction_count(self):
        return self.function_call('transactionCount')

    @property
    def required(self):
        return self.function_call('required')

    @property
    def max_owner_count(self):
        return self.function_call('MAX_OWNER_COUNT')

    def get_submit_transaction_id(self, transaction):
        args = self.get_events_args('Submission', transaction)
        if not args:
            return None
        return args[0]['transactionId']

    def submit_transaction(self,
             sign_callback,
             from_address,
             to_address,
             data      = "",
             value     = 0,
             unit      = 'wei',
             gas_limit = 0,
             gas_price = 0):

        from_address = self._network.Address(from_address)
        to_address   = self._network.Address(to_address)
        value        = self._network.web3.toWei(value, unit)

        return self.transaction(
            sign_callback,
            from_address,
            'submitTransaction',
            to_address,
            value,
            data,
            gas_limit = gas_limit,
            gas_price = gas_price) 

    def confirm_transaction(self,
             sign_callback,
             from_address,
             id_,
             gas_limit = 0,
             gas_price = 0):

        from_address = self._network.Address(from_address)
        id_ = int(id_)

        return self.transaction(
            sign_callback,
            from_address,
            'confirmTransaction',
            id_,
            gas_limit = gas_limit,
            gas_price = gas_price)



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
