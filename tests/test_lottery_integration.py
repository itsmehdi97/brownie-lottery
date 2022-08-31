import time
import pytest

from web3 import Web3
from brownie import config

from scripts.utils import LOCAL_BLLOCKCHAIN_ENVS, get_contract
from scripts.utils import get_account



@pytest.fixture(autouse=True, scope="module")
def skip_for_local_envs(active_network):
    if active_network in LOCAL_BLLOCKCHAIN_ENVS:
        pytest.skip()


def test_can_choose_winner(lottery, active_network, account):
    assert lottery.currentState() == 0
    tx = lottery.createNewLottery({"from": account})
    assert lottery.currentState() == 1

    tx.wait(1)

    lottery.enter({"from": account, "value": lottery.getEnteranceFee() + 100})
    # lottery.enter({"from": account, "value": Web3.toWei(0.03, "ether")})
    # lottery.enter({"from": account, "value": Web3.toWei(0.03, "ether")})

    assert lottery.players(0)


    lottery_balance = lottery.balance()
    winner_balance_before_win = account.balance()

    coordinator = get_contract("vrf_coordinator")
    sub_id = config["networks"][active_network]["subId"]
    print("subid#", sub_id)
    tx = coordinator.addConsumer.transact(sub_id, lottery.address, {"from": account})
    tx.wait(1)

    lottery.closeLottery(sub_id, {"from": account})
    assert lottery.currentState() == 2

    time.sleep(60)

    assert lottery.winner() == account
    assert lottery.balance() == 0
    assert account.balance() == lottery_balance + winner_balance_before_win
