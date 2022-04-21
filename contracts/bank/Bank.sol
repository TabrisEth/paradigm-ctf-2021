pragma solidity 0.4.24;

contract ERC20Like {
    function transfer(address dst, uint256 qty) public returns (bool);

    function transferFrom(
        address src,
        address dst,
        uint256 qty
    ) public returns (bool);

    function approve(address dst, uint256 qty) public returns (bool);

    function balanceOf(address who) public view returns (uint256);
}

contract Bank {
    address public owner; // slot 0
    address public pendingOwner; // slot 1

    struct Account {
        string accountName;
        uint256 uniqueTokens;
        mapping(address => uint256) balances;
    }

    // 根据<存储布局>可以分析出：
    // accounts 为字典mapping存储布局，key的位置是keccak256(key.slot)，则：accounts[addr] = keccak(addr . 2)
    // accounts[addr] 的值为动态数组，起始位置就是：keccak(addr . 2) ， 且一个Account会占用三个存储位置，则：accounts[addr][accountId] = keccak(keccak(addr . 2)) + accountId * 3
    // 然后可以推算出：
    // accounts[addr][accountId].accountName = keccak(keccak(addr . 2)) + accountId * 3 (if string size < 32)
    // accounts[addr][accountId].uniqueTokens = keccak(keccak(addr . 2)) + accountId * 3 + 1
    // accounts[addr][accountId].balances[token]  = keccak( token . [keccak(keccak(addr . 2)) + accountId * 3 + 2] )

    mapping(address => Account[]) public accounts; // slot(2)

    constructor() public {
        owner = msg.sender;
    }

    function depositToken(
        uint256 accountId,
        address token,
        uint256 amount
    ) external {
        require(
            accountId <= accounts[msg.sender].length,
            "depositToken/bad-account"
        );

        // 如果有必要，则创建一个新的account
        if (accountId == accounts[msg.sender].length) {
            accounts[msg.sender].length++;
        }

        Account storage account = accounts[msg.sender][accountId];
        uint256 oldBalance = account.balances[token];

        // 检查是否有足够的的余额，避免发生溢出
        require(oldBalance + amount >= oldBalance, "depositToken/overflow");
        // @ctf we re-enter here and close the account, import to re-enter before uniqueTokens++
        // @ctf 在这里我们可以进行重入攻击并关闭用户，从而避免 uniqueTokens++
        require(
            ERC20Like(token).balanceOf(msg.sender) >= amount,
            "depositToken/low-sender-balance"
        );

        // increment counter for unique tokens if necessary
        if (oldBalance == 0) {
            account.uniqueTokens++;
        }

        // update the balance
        account.balances[token] += amount;

        // transfer the tokens in
        // 将 token 的特定金额 转入为bank合约地址
        uint256 beforeBalance = ERC20Like(token).balanceOf(address(this));
        require(
            ERC20Like(token).transferFrom(msg.sender, address(this), amount),
            "depositToken/transfer-failed"
        );
        uint256 afterBalance = ERC20Like(token).balanceOf(address(this));
        require(
            afterBalance - beforeBalance == amount,
            "depositToken/fee-token"
        );
    }

    function withdrawToken(
        uint256 accountId,
        address token,
        uint256 amount
    ) external {
        require(
            accountId < accounts[msg.sender].length,
            "withdrawToken/bad-account"
        );

        Account storage account = accounts[msg.sender][accountId];
        uint256 lastAccount = accounts[msg.sender].length - 1;
        uint256 oldBalance = account.balances[token];

        // 检查用户确实有足够的余额可以提取金额
        require(oldBalance >= amount, "withdrawToken/underflow");
        require(
            ERC20Like(token).balanceOf(address(this)) >= amount,
            "withdrawToken/low-sender-balance"
        );

        // update the balance
        account.balances[token] -= amount;

        // if the user has emptied their balance, decrement the number of unique tokens
        if (account.balances[token] == 0) {
            account.uniqueTokens--;

            // if the user is withdrawing everything from their last account, close it
            // we can't close accounts in the middle of the array because we can't
            // clone the balances mapping, so the user would lose all their balance
            if (account.uniqueTokens == 0 && accountId == lastAccount) {
                accounts[msg.sender].length--;
            }
        }

        // transfer the tokens out
        uint256 beforeBalance = ERC20Like(token).balanceOf(msg.sender);
        require(
            ERC20Like(token).transfer(msg.sender, amount),
            "withdrawToken/transfer-failed"
        );
        uint256 afterBalance = ERC20Like(token).balanceOf(msg.sender);
        require(
            afterBalance - beforeBalance == amount,
            "withdrawToken/fee-token"
        );
    }

    // set the display name of the account
    function setAccountName(uint256 accountId, string name) external {
        require(
            accountId < accounts[msg.sender].length,
            "setAccountName/invalid-account"
        );

        accounts[msg.sender][accountId].accountName = name;
    }

    // close the last account if empty - we need this in case we couldn't automatically close
    // the account during withdrawal
    function closeLastAccount() external {
        // make sure the user has an account
        require(
            accounts[msg.sender].length > 0,
            "closeLastAccount/no-accounts"
        );

        // make sure the last account is empty
        uint256 lastAccount = accounts[msg.sender].length - 1;
        require(
            accounts[msg.sender][lastAccount].uniqueTokens == 0,
            "closeLastAccount/non-empty"
        );

        // close the account
        accounts[msg.sender].length--;
    }

    // get info about the account
    function getAccountInfo(uint256 accountId)
        public
        view
        returns (string, uint256)
    {
        require(
            accountId < accounts[msg.sender].length,
            "getAccountInfo/invalid-account"
        );

        return (
            accounts[msg.sender][accountId].accountName,
            accounts[msg.sender][accountId].uniqueTokens
        );
    }

    // get the balance of a token
    function getAccountBalance(uint256 accountId, address token)
        public
        view
        returns (uint256)
    {
        require(
            accountId < accounts[msg.sender].length,
            "getAccountBalance/invalid-account"
        );

        return accounts[msg.sender][accountId].balances[token];
    }

    // transfer ownership to a new address
    function transferOwnership(address newOwner) public {
        require(msg.sender == owner);

        pendingOwner = newOwner;
    }

    // accept the ownership transfer
    function acceptOwnership() public {
        require(msg.sender == pendingOwner);

        owner = pendingOwner;
        pendingOwner = address(0x00);
    }
}
