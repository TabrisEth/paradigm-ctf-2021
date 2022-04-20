from web3 import Web3

total_num = 2**256
slot_1 = Web3.solidityKeccak(["uint256"], [1])
print(f"slot_1 hex: {slot_1.hex()}")
slot_1_num = int(slot_1.hex(), 16)
print(f"slot_1_num: {slot_1_num}")

# slot_1_num + x = total_num
x = total_num - slot_1_num
result = x
print(f"result: {result}")
print(hex(result))
