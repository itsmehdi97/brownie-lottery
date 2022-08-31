from unicodedata import decimal
import pytest

from web3 import Web3
from brownie import config
from brownie.exceptions import VirtualMachineError

from scripts.utils import LOCAL_BLLOCKCHAIN_ENVS, get_account, get_contract


@pytest.fixture(autouse=True, scope="module")
def skip_for_non_local_envs(active_network):
    if active_network not in LOCAL_BLLOCKCHAIN_ENVS:
        pytest.skip()


def test_lottery_enterancefee(lottery, active_network):
    # if active_network not in LOCAL_BLLOCKCHAIN_ENVS:
    #     pytest.skip()

    decimals = config["networks"][active_network]["decimals"]
    initialAnswer = config["networks"][active_network]["initialAnswer"]

    enterance_fee_usd = lottery.enteranceFeeUsd()
    expected = enterance_fee_usd/(initialAnswer/10**decimals)

    enterance_fee = lottery.getEnteranceFee()
    
    assert enterance_fee == expected


def test_create_new_lottery(lottery):
    assert lottery.currentState() == 0  # sanity check

    lottery.createNewLottery()

    assert lottery.currentState() == 1


def test_enter_closed_lottery(lottery, account):
    assert lottery.currentState() == 0  # sanity check

    with pytest.raises(VirtualMachineError):
        lottery.enter({
            "from": account,
            "value": lottery.getEnteranceFee() + 10000
        })


def test_enter_with_low_fund(lottery, account):
    lottery.createNewLottery()

    with pytest.raises(VirtualMachineError):
        lottery.enter({
            "from": account,
            "value": lottery.getEnteranceFee() - 10000
        })


def test_enter_lottery(lottery, account):
    lottery.createNewLottery()

    lottery.enter({
        "from": account,
        "value": lottery.getEnteranceFee() + 10000
    })
    assert lottery.players(0) == account


def test_lottery_correctly_select_winner(lottery, account):
    lottery.createNewLottery()
    assert lottery.currentState() == 1

    lottery.enter({
        "from": get_account(index=0),
        "value": lottery.getEnteranceFee() + 10000})
    lottery.enter({
        "from": get_account(index=1),
        "value": lottery.getEnteranceFee() + 10000})
    lottery.enter({
        "from": get_account(index=2),
        "value": lottery.getEnteranceFee() + 10000})

    winner_index = 2

    lottery_balance = lottery.balance()
    winner_balance_before_win = get_account(index=winner_index).balance()

    coordinator = get_contract("vrf_coordinator")
    sub_id = coordinator.createSubscription({"from": account}).return_value
    coordinator.addConsumer(sub_id, lottery.address, {"from": account})

    tx = lottery.closeLottery(sub_id, {"from": account})
    assert lottery.currentState() == 2

    request_id = tx.events["RequestedRandomness"]["requestId"]

    coordinator.fundSubscription(sub_id, Web3.toWei(10, "ether"), {"from": account})
    coordinator.fulfillRandomWords(request_id, lottery.address)

    assert lottery.winner() == get_account(index=winner_index)
    assert lottery.balance() == 0
    assert get_account(index=winner_index).balance() == lottery_balance + winner_balance_before_win
