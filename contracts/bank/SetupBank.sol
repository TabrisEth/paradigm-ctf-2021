pragma solidity 0.4.24;

import "./Bank.sol";

contract IWETH9 is ERC20Like {
    function deposit() public payable;
}

contract SetupBank {
    IWETH9 public weth;
    Bank public bank;

    constructor(address weth9_addr) public payable {
        require(msg.value == 50 ether);
        require(weth9_addr != address(0));
        weth = IWETH9(weth9_addr);

        bank = new Bank();

        weth.deposit.value(msg.value)();
        weth.approve(address(bank), uint256(-1));
        bank.depositToken(0, address(weth), weth.balanceOf(address(this)));
    }

    function isSolved() external view returns (bool) {
        return weth.balanceOf(address(bank)) == 0;
    }
}
