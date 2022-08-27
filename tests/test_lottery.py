import pytest

from web3 import Web3
from brownie import Lottery, accounts, config, network


@pytest.fixture
def lottery():
    return Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": accounts[0]})


def test_lottery_enterancefee(lottery):
    enterance_fee = lottery.getEnteranceFee()
    
    assert enterance_fee > Web3.toWei(0.03, "ether")
    assert enterance_fee < Web3.toWei(0.04, "ether")


def test_create_new_lottery(lottery):
    assert lottery.currentState() == 0  # sanity check

    lottery.createNewLottery()

    assert lottery.currentState() == 1
