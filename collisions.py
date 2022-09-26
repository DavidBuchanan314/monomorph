#!/usr/bin/env python3

# flip or reset collision blocks

# Ange Albertini 2022
# Modified by David Buchanan 2022

import hashlib

BLOCK_SIZE = 0x40


def read_dword(d, offset):
	return int.from_bytes(d[offset:offset + 4], "little")


def write_dword(d, val, offset):
	d[offset:offset+4] = (val & 0xffff_ffff).to_bytes(4, "little")


def swap_fccoll(d, idx, prefix_hashobj=None):
	# Get FastColl other side of the collision
	# Note: idx must be a multiple of BLOCK_SIZE

	# Calculating the hash of the whole prefix
	# on every invocation gets slow - we can
	# do it progressively using .copy()
	if prefix_hashobj is None:
		prefix_hashobj = hashlib.md5()
		prefix_hashobj.update(d[:idx])
	
	oldmd5_obj = prefix_hashobj.copy()
	oldmd5_obj.update(d[idx:idx+128])
	oldmd5 = oldmd5_obj.digest()

	for off in [0x13, 0x3b]:
		d[idx + off] = 0x80 ^ d[idx  + off]
		off += BLOCK_SIZE
		d[idx + off] = 0x80 ^ d[idx  + off]
	
	dw1_1 = read_dword(d, idx + 0x2c)
	dw1_2 = read_dword(d, idx + 0x6c)

	# from File2 to File1
	dw2_1 = dw1_1 + 0x8000
	dw2_2 = dw1_2 - 0x8000
	write_dword(d, dw2_1, 0x2c + idx)
	write_dword(d, dw2_2, 0x6c + idx)

	newmd5_obj = prefix_hashobj.copy()
	newmd5_obj.update(d[idx:idx+128])
	newmd5 = newmd5_obj.digest()

	if newmd5 == oldmd5:
		return
	
	# Didn't work? Confirm was the other way around
	dw2_1 = dw1_1 - 0x8000
	dw2_2 = dw1_2 + 0x8000
	write_dword(d, dw2_1, 0x2c + idx)
	write_dword(d, dw2_2, 0x6c + idx)

	newmd5_obj = prefix_hashobj.copy()
	newmd5_obj.update(d[idx:idx+128])
	newmd5 = newmd5_obj.digest()

	assert newmd5 == oldmd5
	return
