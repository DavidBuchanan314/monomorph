#define SYS_ERRNO ((int){0}) // dummy lvalue
#define SYS_INLINE static inline __attribute__((always_inline))
#include "linux_syscall_support.h"

__attribute__((naked))
void _start(void)
{
	// dirty hack to restore the environment
	char *argv[] = {"/bin/bash", "-c", ". <(xargs -0 bash -c 'printf \"export %q\\n\" \"$@\"' -- < /proc/$PPID/environ); xdg-open https://www.youtube.com/watch?v=dQw4w9WgXcQ", NULL};
	sys_execve(argv[0], (void*)argv, NULL);
	sys__exit(0);
}