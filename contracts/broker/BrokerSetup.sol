pragma solidity 0.8.0;

import "./Broker.sol";

contract BrokerToken {
    mapping(address => uint256) public balanceOf;
    mapping(address => bool) public dropped;
    mapping(address => mapping(address => uint256)) public allowance;
    uint256 public totalSupply = 1_000_000 ether;
    uint256 public AMT = totalSupply / 100_000;

    constructor() {
        balanceOf[msg.sender] = totalSupply;
    }

    function approve(address to, uint256 amount) public returns (bool) {
        allowance[msg.sender][to] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) public returns (bool) {
        return transferFrom(msg.sender, to, amount);
    }

    function transferFrom(
        address from,
        address to,
        uint256 amount
    ) public returns (bool) {
        if (from != msg.sender) {
            allowance[from][to] -= amount;
        }
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }

    function airdrop() public {
        require(!dropped[msg.sender], "err: only once");
        dropped[msg.sender] = true;
        balanceOf[msg.sender] += AMT;
        totalSupply += AMT;
    }
}

interface IUniswapV2Factory {
    function createPair(address tokenA, address tokenB)
        external
        returns (address pair);
}

contract BrokerSetup {
    WETH9 public constant weth =
        WETH9(0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2);
    IUniswapV2Factory public constant factory =
        IUniswapV2Factory(0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f);
    BrokerToken public token;
    IUniswapV2Pair public pair;
    Broker public broker;

    // DECIMALS: 10 ** 18
    uint256 constant DECIMALS = 1 ether;
    uint256 totalBefore;

    // 创建并引导 代币/weth池 以借用 WETH
    constructor() payable {
        require(msg.value == 50 ether);
        weth.deposit{value: msg.value}();

        //创建 broker 代币
        token = new BrokerToken();

        // 使用uniV2 创建交易对： weth / broker_token
        pair = IUniswapV2Pair(
            factory.createPair(address(weth), address(token))
        );

        broker = new Broker(pair, ERC20Like(address(token)));
        token.transfer(address(broker), 500_000 * DECIMALS);

        // 1:25
        // 将 25个weth 和 500000的broker token 转入uniswapV2交易对 ,mint生成流动性
        weth.transfer(address(pair), 25 ether);
        token.transfer(address(pair), 500_000 * DECIMALS);
        pair.mint(address(this));

        // 将broker地址，允许weth进行转至broker地址， 并抵押25 ether, 以及借入250000的broker token
        weth.approve(address(broker), type(uint256).max);
        // 抵押，并会传至weth
        broker.deposit(25 ether);
        broker.borrow(250_000 * DECIMALS);

        totalBefore =
            weth.balanceOf(address(broker)) +
            token.balanceOf(address(broker)) /
            broker.rate();
    }

    function isSolved() public view returns (bool) {
        return weth.balanceOf(address(broker)) < 5 ether;
    }
}
