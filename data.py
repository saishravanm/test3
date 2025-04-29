from fixedint import UInt16, UInt32, UInt64

# --- Custom BCH(82, 61) Implementation ---
class BCH82_61:
    def __init__(self):
        # COSPAS-SARSAT specified BCH(82,61) generator polynomial (degree 21)
        g_str = "100110110111010110001"
        # Ensure polynomial is 22 bits long (21 + 1 for leading coefficient)
        self.g = [int(b) for b in g_str.zfill(22)]

    def encode(self, data_bits):
        # Validate input length: BCH(82,61) expects exactly 61 data bits
        if len(data_bits) != 61:
            raise ValueError("Data must be 61 bits long")
        
        # Pad with 21 zeros for space where parity bits will go
        padded = data_bits + [0] * 21
        # Copy of padded bits to use for polynomial division
        remainder = padded[:]

        # Perform binary polynomial division (mod-2 division)
        for i in range(len(data_bits)):
            if remainder[i] == 1:
                for j in range(len(self.g)):
                    remainder[i + j] ^= self.g[j]

        # Return full codeword (original 61 bits + final 21-bit remainder)
        return data_bits + remainder[-21:]

# Converts byte data into a list of bits, zero-padded to 'total_bits' length
def bits_from_bytes(byte_data, total_bits):
    bit_string = bin(int.from_bytes(byte_data, byteorder='big'))[2:].zfill(total_bits)
    return [int(b) for b in bit_string]

# Converts a list of bits into a byte array
def bits_to_bytes(bits):
    value = int("".join(map(str, bits)), 2)
    byte_len = (len(bits) + 7) // 8
    return value.to_bytes(byte_len, byteorder='big')

# Bitwise right shift for a list of bits
def bitwise_right_shift(bits, shift):
    as_int = int("".join(map(str, bits)), 2)
    shifted = as_int >> shift
    return [int(b) for b in bin(shifted)[2:].zfill(len(bits) - shift)]



country_codes = {
    4: "AFG", 8: "ALB", 12: "DZA", 20: "AND", 24: "AGO",
    32: "ARG", 36: "AUS", 40: "AUT", 48: "BHR", 50: "BGD",
    56: "BEL", 64: "BTN", 68: "BOL", 72: "BWA", 76: "BRA",
    84: "BLZ", 100: "BGR", 108: "BDI", 116: "KHM", 120: "CMR",
    124: "CAN", 132: "CPV", 144: "LKA", 152: "CHL", 156: "CHN",
    170: "COL", 178: "COG", 180: "COD", 188: "CRI", 191: "HRV",
    196: "CYP", 203: "CZE", 208: "DNK", 214: "DOM", 218: "ECU",
    222: "SLV", 231: "ETH", 233: "EST", 242: "FJI", 246: "FIN",
    250: "FRA", 268: "GEO", 270: "GMB", 276: "DEU", 288: "GHA",
    300: "GRC", 320: "GTM", 324: "GIN", 328: "GUY", 332: "HTI",
    340: "HND", 348: "HUN", 356: "IND", 360: "IDN", 364: "IRN",
    368: "IRQ", 372: "IRL", 376: "ISR", 380: "ITA", 392: "JPN",
    400: "JOR", 404: "KEN", 408: "PRK", 410: "KOR", 414: "KWT",
    417: "KGZ", 418: "LAO", 422: "LBN", 426: "LSO", 428: "LVA",
    430: "LBR", 434: "LBY", 440: "LTU", 442: "LUX", 450: "MDG",
    454: "MWI", 458: "MYS", 462: "MDV", 466: "MLI", 470: "MLT",
    478: "MRT", 480: "MUS", 484: "MEX", 496: "MNG", 498: "MDA",
    504: "MAR", 508: "MOZ", 512: "OMN", 516: "NAM", 524: "NPL",
    528: "NLD", 533: "ABW", 540: "NCL", 554: "NZL", 558: "NIC",
    566: "NGA", 578: "NOR", 586: "PAK", 591: "PAN", 598: "PNG",
    600: "PRY", 604: "PER", 608: "PHL", 616: "POL", 620: "PRT",
    634: "QAT", 642: "ROU", 643: "RUS", 646: "RWA", 662: "LCA",
    670: "VCT", 682: "SAU", 688: "SRB", 690: "SYC", 694: "SLE",
    702: "SGP", 704: "VNM", 710: "ZAF", 724: "ESP", 752: "SWE",
    756: "CHE", 764: "THA", 780: "TTO", 788: "TUN", 800: "UGA",
    804: "UKR", 807: "MKD", 818: "EGY", 826: "GBR", 834: "TZA",
    840: "USA", 850: "VIR", 854: "BFA", 858: "URY", 860: "UZB",
    862: "VEN", 887: "YEM", 894: "ZMB"
}

# Printing function for bytes objects
def printBytes(byteData):
    hex_string = " ".join([f"{byte:02X}" for byte in byteData])  # Convert to hex
    print(hex_string)

def leftShift(byteArray, shift):
    for i in range(len(byteArray) - 1):
        byteArray[i] = ((byteArray[i] << shift) | (byteArray[i + 1] >> (8 - shift))) & 0xFF
    byteArray[-1] = (byteArray[-1] << shift) & 0xFF
    return byteArray

def rightShift(byteArray, shift):
    for i in range(len(byteArray) - 1, 0, -1):
        byteArray[i] = ((byteArray[i] >> shift) | (byteArray[i-1] << (8 - shift))) & 0xFF
    byteArray[0] = (byteArray[0] >> shift) & 0xFF
    return byteArray

# Grab the specified bytes from a packet
def grabBytes(byteData, start_bit, end_bit):
    start_byte = start_bit // 8 if start_bit % 8 != 0 else (start_bit // 8) - 1
    end_byte = end_bit // 8 if end_bit % 8 != 0 else (end_bit // 8) - 1
    right_shift = (end_byte + 1) * 8 - end_bit
    left_shift = start_bit - (start_byte * 8 + 1)
    bit_length = end_bit - start_bit + 1
    temp_bytes = bytearray(byteData[start_byte: end_byte + 1])

    # printBytes(bytes)
    # print("Bytes Section ", start_byte, end_byte, start_bit, end_bit)
    # printBytes(temp_bytes)
    temp_int = int.from_bytes(temp_bytes, byteorder="big")
    
    # print("Right Shift ", right_shift)
    temp_int = (temp_int >> right_shift)
    rightShift(temp_bytes, right_shift)

    # print(hex(temp_int))
    # print("Masking")
    mask = ((1 << bit_length) - 1)
    temp_int = temp_int & mask
    # print(hex(mask))
    # print(hex(temp_int))
    # print("Reset")
    temp_int = temp_int << (right_shift)
    leftShift(temp_bytes, right_shift)
    # print(hex(temp_int))
    # print("Left Shift ", left_shift)
    temp_int = temp_int << left_shift
    leftShift(temp_bytes, left_shift)
    # print(hex(temp_int))


    # temp_bytes = temp_int.to_bytes((temp_int.bit_length() + 7) // 8, byteorder='big')
    end_byte = bit_length // 8 + 1 if bit_length % 8 != 0 else bit_length // 8
    return bytes(temp_bytes[0:end_byte])

class CountryCode: 
    def __init__(self, bytes):
        self.digits = int.from_bytes(bytes) >> 6
        self.code = country_codes.get(self.digits, "UNK")

    def __str__(self):
        return f"${self.code} (${self.digits})"

# Initialize the data value

class Coordinate: 
    def __init__(self, loc_bytes, diff_bytes):
        self.ns = "N" if (int.from_bytes(grabBytes(loc_bytes, 1, 1)) >> 7) == 0 else "S"
        self.ew = "E" if (int.from_bytes(grabBytes(loc_bytes, 11, 11)) >> 7) == 0 else "W"
        
        deg_delta = 0.25
        minute_delta = 1
        second_delta = 4
        self.lat_deg = deg_delta * (int.from_bytes(grabBytes(loc_bytes, 2, 10)) >> 7)
        self.long_deg = deg_delta * (int.from_bytes(grabBytes(loc_bytes, 12, 21)) >> 6)

        self.lat_delta_sign = -1 if (int.from_bytes(grabBytes(diff_bytes, 1, 1)) >> 7) == 0 else 1
        self.long_delta_sign = -1 if (int.from_bytes(grabBytes(diff_bytes, 11, 11)) >> 7) == 0 else 1

        self.lat_minutes = minute_delta * (int.from_bytes(grabBytes(diff_bytes, 2, 6)) >> 3)
        self.lat_seconds = second_delta * (int.from_bytes(grabBytes(diff_bytes, 7, 10)) >> 4)
        self.long_minutes = minute_delta * (int.from_bytes(grabBytes(diff_bytes, 12, 16)) >> 3)
        self.long_seconds = second_delta * (int.from_bytes(grabBytes(diff_bytes, 17, 20)) >> 4)

    def __str__(self):
        return f"{self.ns}-{self.lat_deg} DELTA ({self.lat_delta_sign * self.lat_minutes}:{self.lat_seconds}):{self.ew}-{self.long_deg} DELTA ({self.long_delta_sign * self.long_minutes}:{self.long_seconds})"



class Identification: 
    def __init__(self, bytes, protocol_code):
        # Make variables to hold the values
        self.protocol_code = grabBytes(bytes, 1, 4)

        if protocol_code == 0:
            STANDARD = [b'\x20', b'\x30', b'\x40', b'\x50', b'\x60', b'\x70', b'\xC0', b'\xE0']
            NATIONAL = [b'\x80', b'\xA0', b'\xB0', b'\xF0']
            RLS = b'\xD0'
            ELT_DT = b'\x90'
            # Set Protocol Name
            if self.protocol_code in STANDARD:
                self.protocol = "STANDARD LOCATION PROTOCOL"
            elif self.protocol_code in NATIONAL:
                self.protocol = "NATIONAL LOCATION PROTOCOL"
            elif self.protocol_code == RLS:
                self.protocol = "RLS LOCATION PROTOCOL"
            elif self.protocol_code == ELT_DT: 
                self.protocol = "ELT-DT LOCATION PROTOCOL"
            else: 
                x = 1
                # print("ERROR: Corrupted Identification Protocol/Information")
        elif protocol_code == 1:
            self.protocol = "USER-LOCATION PROTOCOL"
        else:
            print("ERROR: Corrupted protocol code")




class HexData: 
    def read(self):
        self.hexData = self.hex_file.read(18)
        self.bit_synch = grabBytes(self.hexData, 1, 15)
        if(self.bit_synch != b'\xFF\xFE'):
            print("ERROR: Bit Synch Failure")
        self.frame_sync = grabBytes(self.hexData, 16, 24)
        if(self.frame_sync != b'\x17\x80'):
            print("ERROR: Non-normal Beacon Operation")

        # BCH-1 Check (using custom encoder)
        self.pdf1 = grabBytes(self.hexData, 25, 85)
        self.bch1 = grabBytes(self.hexData, 86, 106)
        print(self.bch1.hex())

        raw_bits = bits_from_bytes(self.hexData, len(self.hexData) * 8)
        shifted_bits = bitwise_right_shift(raw_bits, 3)
        data_bits = shifted_bits[24:85]  # Bits 25-85 after 3-bit shift

        bch1_encoder = BCH82_61()
        codeword = bch1_encoder.encode(data_bits)

        bch_bits = codeword[61:]
        bch1_calc = bits_to_bytes(bch_bits)

        print("PDF1 Bits      :", "".join(map(str, data_bits)))
        print("Calc BCH Bits  :", "".join(map(str, bch_bits)))
        print(bch1_calc.hex())
        print("Error Check (PDF-1):")

        # BCH-2 Check untouched
        self.pdf2 = grabBytes(self.hexData, 107, 132)
        self.bch2 = grabBytes(self.hexData, 133, 144)

        self.format = int.from_bytes(grabBytes(self.hexData, 25, 25)) >> 7
        self.protocol = int.from_bytes(grabBytes(self.hexData, 26, 26)) >> 7
        self.country_code = CountryCode(grabBytes(self.hexData, 27, 36))
        self.identification = Identification(grabBytes(self.hexData, 37, 64), self.protocol)
        self.coords = Coordinate(grabBytes(self.hexData, 65, 85), grabBytes(self.hexData, 113, 132))
        self.supp_data = grabBytes(self.hexData, 107, 106)

    def print(self):
        print("Data Stored: ")
        printBytes(self.hexData)
        print("----------------------------------------")
        print("Format: ", self.format)
        print("Protocol: ", self.protocol)
        print("Country Code: ", self.country_code)
        print("Coordinates: ", self.coords)

    def close(self):
        self.hex_file.close()

    def __init__(self, filename):
        if isinstance(source, (bytes, bytearray)):
            self.hex_file = io.BytesIO(source)
        else:
            self.hex_file = open(source, "rb")
        self.read()

    def __del__(self):
        self.close()