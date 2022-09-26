BANNER = """\
                                                
                                                
                                                
    ════════════════════════════════════╦═══    
     ╔═╦═╗ ╔═╗ ╔═╗ ╔═╗ ╔═╦═╗ ╔═╗ ╔══╔═╗ ╠═╗     
    ═╩ ╩ ╩═╚═╝═╩ ╩═╚═╝═╩ ╩ ╩═╚═╝═╩  ╠═╝═╩ ╩═    
    ════════════════════════════════╩═══════    
                                  By Retr0id    
                                                
    ═══ MD5-Monomorphic Shellcode Packer ═══    
                                                
                                                
"""


from collisions import swap_fccoll
import hashlib
import zlib

def set_bit(data, offset, value, hashobj=None):
	if (data[offset + 0x13] >> 7) ^ value:
		assert((offset % 64) == 0)
		swap_fccoll(data, offset, hashobj)

def compress_raw(data):
	c = zlib.compressobj(level=9, wbits=-15)
	return c.compress(data) + c.flush(zlib.Z_FINISH)

def encode_payload(input_filename, output_filename, payload, activate=True):
	print(f"[+] Loading input binary from {input_filename!r}")
	monomorph = bytearray(open(input_filename, "rb").read())
	orig_hash = hashlib.md5(monomorph).digest()
	print(f"[+] Original MD5: {orig_hash.hex()}")

	compressed_payload = compress_raw(payload)

	idx = monomorph.index((0xdeadbeef).to_bytes(4, "little"))
	max_payload_len = int.from_bytes(monomorph[idx+4:idx+4+4], "little")

	print("[+] Max payloax size:", max_payload_len)
	print("[+] Setting config:")
	print("    - Raw payload size:", len(payload))
	print("    - Compressed payload size:", len(compressed_payload))
	print("    - Activated:", activate)
	assert(len(compressed_payload) <= max_payload_len)

	idx += 128 # skip header

	set_bit(monomorph, idx, activate) # activate
	idx += 128

	buffer = len(payload).to_bytes(4, "little") + compressed_payload + bytes(max_payload_len - len(compressed_payload))

	hashobj = hashlib.md5()
	hashobj.update(monomorph[:idx])
	for byte in buffer:
		for bit in range(8):
			set_bit(monomorph, idx, (byte >> bit) & 1, hashobj)
			hashobj.update(monomorph[idx:idx+128])
			idx += 128

	final_hash = hashlib.md5(monomorph).digest()
	print(f"[+] Final MD5: {final_hash.hex()}")
	assert(orig_hash == final_hash)

	print(f"[+] Saving to {output_filename!r}")
	with open(output_filename, "wb") as out:
		out.write(monomorph)

if __name__ == "__main__":
	import sys

	print(BANNER)

	if len(sys.argv) not in [3, 4]:
		print(f"USAGE: python3 {sys.argv[0]} input_file output_file [payload_file]")
		exit()

	input_file = sys.argv[1]
	output_file = sys.argv[2]

	if len(sys.argv) == 4:
		payload = open(sys.argv[3], "rb").read()
		encode_payload(input_file, output_file, payload)
	else:
		print("[+] No payload specified. Creating benign executable.")
		encode_payload(input_file, output_file, b"", activate=False)