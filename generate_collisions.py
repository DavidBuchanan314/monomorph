from fastercoll import fastercoll
from tqdm import tqdm

monomorph = bytearray(open("loader/monomorph", "rb").read())

idx = monomorph.index((0xdeadbeef).to_bytes(4, "little"))
max_payload_len = int.from_bytes(monomorph[idx+4:idx+4+4], "little")

num_collisions = 1 + 32 + max_payload_len * 8

print(f"generating {hex(num_collisions)} collisions...")

prefix = monomorph[:idx+128]

for i in tqdm(range(num_collisions), smoothing=0):
	a, b = fastercoll(prefix)
	prefix += a

result = prefix + monomorph[len(prefix):]

with open("bin/monomorph.template", "wb") as out:
	out.write(result)
