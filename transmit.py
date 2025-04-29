import adi
import numpy as np
import time
import math
from commpy.filters import rcosfilter

# ————————————————————————
# CONFIGURATION
TX_FREQUENCY_HZ = 915_000_000    # 915 MHz center
DATA_RATE       = 400            # bits per second (baud)
SAMPLES_PER_BIT = math.ceil(521_000 / DATA_RATE)            # SDR samples per symbol (tweak for performance)
SAMPLE_RATE     = DATA_RATE * SAMPLES_PER_BIT
TX_BW           = SAMPLE_RATE    # RF bandwidth
TX_GAIN         = 0              # Pluto TX gain (dB)
TX_INTERVAL     = 60             # seconds between packets
# ————————————————————————

def calculateBCH(data):
    data = data.copy()
    if len(data) == 26:
        g = np.array([1,0,1,0,1,0,0,1,1,1,0,0,1])
        data = np.append(data, np.zeros(12, dtype=int))
    elif len(data) == 61:
        g = np.array([1,0,0,1,1,0,1,1,0,1,1,0,0,1,1,1,1,0,0,0,1,1])
        data = np.append(data, np.zeros(21, dtype=int))
    else:
        raise ValueError(f"Data must be 26 or 61 bits, got {len(data)} bits")

    while True:
        ones = np.where(data == 1)[0]
        if len(ones) == 0 or ones[0] + len(g) > len(data):
            break
        idx = ones[0]
        data[idx:idx+len(g)] ^= g

    # return the parity suffix
    if len(data) == 38:
        return data[-12:]
    elif len(data) == 82:
        return data[-21:]
    else:
        raise RuntimeError("Unexpected length after BCH divide")

def dec2bin(n, minBits=0):
    n = int(n)
    bits = [int(b) for b in bin(n)[2:]]
    if minBits > len(bits):
        bits = [0] * (minBits - len(bits)) + bits
    return np.array(bits, dtype=int)

def createPacket(lat, lon):
    # Hard-coded HEX ID fields turned into test-protocol packet
    bitSynch       = np.ones(15, dtype=int)
    frameSynch     = np.array([0,0,0,1,0,1,1,1,1], dtype=int)
    formatFlag     = np.array([1], dtype=int)
    protocolFlag   = np.array([0], dtype=int)
    countryCode    = np.array([0,1,0,1,1,1,0,0,0,0], dtype=int)  # USA = 368
    protocolCode   = np.array([1,1,1,0], dtype=int)               # test
    testProtocol   = np.array([0]*23 + [1], dtype=int)            # 24 bits in example
    packet = np.concatenate([
        bitSynch, frameSynch,
        formatFlag, protocolFlag,
        countryCode, protocolCode,
        testProtocol
    ])

    # Latitude PDF-1
    packet = np.concatenate([
        packet,
        np.array([0 if lat >= 0 else 1]),          # N/S
        dec2bin(round(abs(lat)/0.25), 9)           # degrees/0.25
    ])
    # Longitude PDF-1
    packet = np.concatenate([
        packet,
        np.array([0 if lon >= 0 else 1]),          # E/W
        dec2bin(round(abs(lon)/0.25), 10)          # degrees/0.25
    ])

    # First BCH
    bch1 = calculateBCH(packet[24:85])
    packet = np.concatenate([packet, bch1])

    # Validity + Encoded Position + Homing
    packet = np.concatenate([
        packet,
        np.array([1,1,0,1], dtype=int),           # validity = 1101
        np.array([1], dtype=int),                 # encoded position source
        np.array([0], dtype=int)                  # homing 121.5 MHz flag
    ])

    # Lat/Lon offsets PDF-2
    lat_offset = abs(lat) - round(abs(lat)/0.25)*0.25
    lon_offset = abs(lon) - round(abs(lon)/0.25)*0.25

    # Latitude offset sign + minutes + seconds
    packet = np.concatenate([
        packet,
        np.array([1 if lat_offset < 0 else 0], dtype=int),
        dec2bin(math.floor(60*abs(lat_offset)), 5),
        dec2bin(round(60*((60*abs(lat_offset))%1)/4), 4)
    ])
    # Longitude offset sign + minutes + seconds
    packet = np.concatenate([
        packet,
        np.array([1 if lon_offset < 0 else 0], dtype=int),
        dec2bin(math.floor(60*abs(lon_offset)), 5),
        dec2bin(round(60*((60*abs(lon_offset))%1)/4), 4)
    ])

    # Second BCH
    bch2 = calculateBCH(packet[106:132])
    packet = np.concatenate([packet, bch2])

    assert len(packet) == 144, f"Packet should be 144 bits, got {len(packet)}"
    return packet

def transmitPacket(sdr, packet):
    # Map bits → BPSK levels, oversampled
    oneBit  = np.repeat([1.0, -1.0], SAMPLES_PER_BIT//2)
    zeroBit = np.repeat([-1.0, 1.0], SAMPLES_PER_BIT//2)
    symbols = np.hstack([oneBit if bit else zeroBit for bit in packet])

    # RRC shaping
    _, rrc = rcosfilter(132, 0.8, DATA_RATE, SAMPLE_RATE)
    shaped = np.convolve(symbols, rrc, mode='same').astype(np.complex64)
    # scale up for Pluto
    shaped *= (2**14)

    sdr.tx(shaped)

if __name__ == "__main__":
    # Initialize Pluto
    sdr = adi.Pluto(uri='ip:192.168.2.1')   # or "usb:"
    sdr.tx_lo              = TX_FREQUENCY_HZ
    sdr.sample_rate        = int(SAMPLE_RATE)
    sdr.tx_rf_bandwidth    = int(TX_BW)
    sdr.tx_hardwaregain_chan0 = TX_GAIN

    # Your test coordinates
    test_lat = 38.624593
    test_lon = -90.185037

    last_time = 0
    while True:
        now = time.time()
        if now - last_time >= TX_INTERVAL:
            last_time = now
            pkt = createPacket(test_lat, test_lon)
            transmitPacket(sdr, pkt)
            print(f"[{time.strftime('%H:%M:%S')}] Transmitted test packet @ 915 MHz")
        time.sleep(0.1)
