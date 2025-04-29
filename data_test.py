from data import rightShift, leftShift, HexData

hex_reader = HexData("data.bin")
hex_reader.print()

byteData = bytearray(b'\xC8\xFE')


# hex_string = " ".join([f"{byte:02X}" for byte in cc])  # Convert to hex
# print(hex_string)


# hex_string = " ".join([f"{byte:02X}" for byte in file_bytes])  # Convert to hex
# print(hex_string)

# temp_int = int.from_bytes(file_bytes, byteorder="big")
# temp_int = (temp_int >> 8) 
# temp_bytes = temp_int.to_bytes((temp_int.bit_length() + 7) // 8, byteorder="big")
# hex_string = " ".join([f"{byte:02X}" for byte in temp_bytes])  # Convert to hex
# print(hex_string)

# temp_int = temp_int & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
# temp_bytes = temp_int.to_bytes((temp_int.bit_length() + 7) // 8, byteorder="big")
# hex_string = " ".join([f"{byte:02X}" for byte in temp_bytes])  # Convert to hex
# print(hex_string)

# hex_string = " ".join([f"{byte:02X}" for byte in file_bytes])  # Convert to hex
# print(hex_string)
