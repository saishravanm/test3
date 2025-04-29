# beacon_detect.py
import adi
import numpy as np
from data import HexData


SAMPLE_RATE = 1_000_000
FREQUENCY = 915_000_000  # 2.4 GHz
BUFFER_SIZE = 4096
DETECTION_THRESHOLD = 0.01  # Adjust if needed
FRAME_LEN_BYTES = 18
BIT_RATE = 400

def run_beacon_detection(log=None, callback=None):
    def _log(msg):
        if log:
            log(msg)

    result = False
    sdr = None
    try:
        _log("🔌 Connecting to SDR...")
        sdr = adi.Pluto("usb:")
        sdr.rx_enabled_channels = [0]
        sdr.sample_rate = SAMPLE_RATE
        sdr.rx_lo = FREQUENCY
        sdr.rx_rf_bandwidth = SAMPLE_RATE
        sdr.rx_buffer_size = BUFFER_SIZE
        sdr.gain_control_mode = "manual"
        sdr.rx_hardwaregain = 40
        _log("📶 Tuning to 2.4 GHz and capturing signal...")

        while True:
            samples = sdr.rx()
            if samples is None or len(samples) == 0:
                continue
            mag = np.mean(np.abs(samples))
            if mag > DETECTION_THRESHOLD:
                _log(f"⚡ Detected energy (mag={mag:.5f})")
                break

        packet_bytes = demodulate_to_bytes(samples, FRAME_LEN_BYTES)
        if len(packet_bytes) != FRAME_LEN_BYTES:
            raise RuntimeError(f"Expected {FRAME_LEN_BYTES} bytes, got {len(packet_bytes)}")
    
        bin_path = "latest_beacon.bin"
        with open(bin_path, "wb") as f:
            f.write(packet_bytes)
        _log(f"Wrote raw frame to {bin_path}")
    
        beacon = HexData(packet_bytes)
        data = {
            "Format": beacon.format,
            "Protocol": beacon.protocol,
            "Country": str(beacon.country_code),
            "Coordinates": str(beacon.coords)
        }
    
        _log("Packet Decoded Successfully")
        callback(data)
    
    except Exception as e:
        _log(f"💥 Error: {e}")
        
    finally:
        if sdr:
            try:
                sdr.rx_destroy_buffer()
            except:
                pass
            del sdr
        if callback:
            callback(result)


def demodulate_to_bytes(samples, length):
    
    # remove DC
    samples = samples - np.mean(samples)
    
    # how many SDR samples per bit
    spb = int(SAMPLE_RATE/BIT_RATE)
    num_bits = length * 8
    required = spb * num_bits
    if len(samples) < required:
        raise RuntimeError(f"Need at least {required} samples, got {len(samples)}")
    
    # bit decisions
    bits = np.empty(num_bits, dtype = np.uint8)
    for i in range(num_bits):
        start = i * spb
        end = start + spb
        metric = np.sum(np.real(samples[start:end]))
        bits[i] = 1 if metric > 0 else 0 
        
    # pack into bytes (msb in each byte)
    packed = np.packbits(bits)
    packet = packed.to_bytes()
    
    # sanity check 
    if len(packet) != length:
        raise RuntimeError(f"Packed {len(packet)} bytes, expected {length}")
    return packet