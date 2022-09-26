import os
import sys

def elf_to_shellcode(input_path, output_path):
	# https://github.com/gamozolabs/elfloader
	os.system(f"elfloader {input_path} {input_path}.felf")

	felf = open(f"{input_path}.felf", "rb")
	assert(felf.read(8) == b"FELF0001")
	entry = int.from_bytes(felf.read(8), "little")
	base = int.from_bytes(felf.read(8), "little")
	assert(base == 0)

	# create a jump to the entrypoint
	trampoline = b"\xe9" + (entry + 0x1000 - 5).to_bytes(4, "little")
	trampoline += bytes(0x1000 - len(trampoline))

	shellcode = trampoline + felf.read()
	with open(output_path, "wb") as out:
		out.write(shellcode)

if __name__ == "__main__":
	elf_to_shellcode(sys.argv[1], sys.argv[2])