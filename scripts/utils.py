from brownie import network, accounts, config, Contract
from brownie import MockV3Aggregator, VRFCoordinatorV2Mock
from eth_typing import abi


FORKED_LOCAL_ENVS = {"mainnet-fork"}
LOCAL_BLLOCKCHAIN_ENVS = {"development", "ganache-local"}

CONTRACT_MOCKS = {
   "eth_usd_price_feed": MockV3Aggregator,
   "vrf_coordinator": VRFCoordinatorV2Mock,
}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in FORKED_LOCAL_ENVS | LOCAL_BLLOCKCHAIN_ENVS:
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name, *args):
    contract_type = CONTRACT_MOCKS[contract_name]
    if network.show_active() in LOCAL_BLLOCKCHAIN_ENVS:
        if not len(contract_type):
            deploy_mock_from(contract_type, *args)
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, abi=contract_type.abi)
    return contract


def deploy_mock_from(contract, *args):
    account = get_account()
    contract.deploy(*args, {"from": account})
