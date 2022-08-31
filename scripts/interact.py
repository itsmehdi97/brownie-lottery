from brownie import network, config
from brownie import Lottery

from scripts.utils import get_account


def lottery_start():
    Lottery[-1].createNewLottery({"from": get_account()})

def lottery_enter(fee=None):
    acc = get_account()
    enterance_fee = lottery_enterance_fee()
    fee = fee or (enterance_fee + 1000)
    tx_receipt = Lottery[-1].enter({
        "from": acc,
        "value": fee
    })
    tx_receipt.wait(1)
    print(f"{acc} entered the lottery.")


def lottery_enterance_fee():
    fee = Lottery[-1].getEnteranceFee()
    print(fee)
    return fee
