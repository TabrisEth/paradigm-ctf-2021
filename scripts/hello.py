from brownie import SetupHello, Contract, Hello
from web3 import Web3
import time
from scripts.helpful_scripts import get_accounts


def deploy():
    global deployer, setupHello, helloAddr, hello, solved
    [deployer] = get_accounts()
    solved = False

    # 开始部署
    setupHello = SetupHello.deploy({"from": deployer})
    helloAddr = setupHello.hello()
    hello = Contract.from_abi(Hello._name, helloAddr, Hello.abi)


def attack():
    # 攻击代码写到这里
    hello.solve({"from": deployer}).wait(1)
    return


def check():
    # 检测攻击是否完成： 不能继续借贷
    print("running func check..")
    try:
        assert hello.solved()
        print("success!")
    except:
        time.sleep(1)
        print("Not pass yet ;(")

    return


def main():
    deploy()
    attack()
    check()
