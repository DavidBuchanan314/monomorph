all: hashquine.bin rickroll.bin

%.bin: %.elf
	python3 elf_to_shellcode.py $< $@

%.elf: %.c
	gcc $< -o $@ -static-pie -nostdlib -s -Os -fcf-protection=none