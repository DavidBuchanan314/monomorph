#define SYS_ERRNO ((int){0}) // dummy lvalue
#define SYS_INLINE static inline __attribute__((always_inline))
#include "linux_syscall_support.h"

static char message[] = "My MD5 is: 3cebbe60d91ce760409bbe513593e401\n";

__attribute__((naked))
void _start(void)
{
	sys_write(1, message, sizeof(message) - 1);
	sys__exit(0);
}