import pandas as pd

def calculate_can_crc(bits):

    augmented_bits = bits + [0] * 15
    
    divisor = [1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1]
    remainder = list(augmented_bits)
    
    for i in range(len(bits)):
        if remainder[i] == 1:
            for j in range(len(divisor)):
                remainder[i + j] ^= divisor[j]

    final_crc_bits = remainder[-15:]
    
    crc_val = 0
    for b in final_crc_bits:
        crc_val = (crc_val << 1) | b
    return crc_val

def to_bits(value, n_bits):
    bits = []
    
    for i in range(n_bits - 1, -1, -1):
        
        shifted_value = value >> i
        
        bit = shifted_value & 1
        
        bits.append(bit)
        
    return bits

def validate_can_frame(row):
    try:
        id_val = int(row['id'], 16)
        ide = int(row['ide'])
        rtr = int(row['rtr'])
        dlc = int(row['dlc'])
        data_str = str(row['data']).strip() if not pd.isna(row['data']) else ""
        provided_crc = int(row['crc'], 16)

        if ide == 0 and id_val > 0x7FF:
            return False, f"Invalid ID (Standard > 0x7FF): {row['id']}"
        elif ide == 1 and id_val > 0x1FFFFFFF:
            return False, f"Invalid ID (Extended > 0x1FFFFFFF): {row['id']}"
        
        data_bytes = data_str.split() if data_str else []
        expected_bytes = dlc if dlc <= 8 else 8
        if len(data_bytes) != expected_bytes:
            return False, f"DLC Mismatch (DLC: {dlc}, Data Bytes: {len(data_bytes)})"

        bits = [0] # SOF
        if ide == 0:
            bits.extend(to_bits(id_val, 11))
            bits.append(rtr)
            bits.extend([0, 0]) # IDE bit (0) and r0 bit (0)
            bits.extend(to_bits(dlc, 4))
        else:
            id_a = (id_val >> 18) & 0x7FF
            id_b = id_val & 0x3FFFF
            bits.extend(to_bits(id_a, 11))
            bits.extend([1, 1]) # SRR and IDE
            bits.extend(to_bits(id_b, 18))
            bits.append(rtr)
            bits.extend([0, 0]) # r1 and r0
            bits.extend(to_bits(dlc, 4))

        for byte_str in data_bytes:
            bits.extend(to_bits(int(byte_str, 16), 8))

        calc_crc = calculate_can_crc(bits)
        if calc_crc != provided_crc:
            return False, f"CRC Mismatch (Calculated: 0x{calc_crc:04X}, Provided: 0x{row['crc']})"
        
        return True, "Valid"

    except Exception as e:
        return False, f"Parsing Error: {str(e)}"

df = pd.read_csv('can_frames.csv')

for _, row in df.iterrows():
    is_valid, reason = validate_can_frame(row)
    status = "no error" if is_valid else "error"
    error_msg = f"- {reason}" if not is_valid else ""
    print(f"{row['timestamp']} {row['id']} {status} {error_msg}")