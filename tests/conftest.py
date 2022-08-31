import pytest

from brownie import config, network

from scripts.deploy import deploy_lottery
from scripts.utils import get_account


@pytest.fixture(scope="session")
def active_network():
    return network.show_active()


@pytest.fixture(scope="session")
def account():
    return get_account()


@pytest.fixture
def lottery():
    return deploy_lottery()
