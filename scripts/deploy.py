from brownie import network, config
from brownie import Lottery

from scripts.utils import get_account, get_contract



def deploy_lottery():
    active_network = network.show_active()
    network_conf = config["networks"][active_network]

    return Lottery.deploy(
        get_contract("eth_usd_price_feed", network_conf["decimals"], network_conf["initialAnswer"]).address,
        get_contract("vrf_coordinator", 1, 1).address,
        # network_conf["subId"],
        network_conf["keyHash"],
        network_conf["callBackGasLimit"],
        {"from": get_account()},
        publish_source=network_conf.get("verify", False))


def main():
    deploy_lottery()
