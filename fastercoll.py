import subprocess
import psutil

N_PROCS = 16

def fastercoll(prefix):
	with open("/tmp/prefix.bin", "wb") as pf:
		pf.write(prefix)
	procs_list = []
	for i in range(N_PROCS):
		subproc = subprocess.Popen([
			"./fastcoll/fastcoll",
			"/tmp/prefix.bin",
			"-o",
			f"/tmp/out{i}a.bin",
			f"/tmp/out{i}b.bin"
		], stdout=subprocess.DEVNULL)
		procs_list.append(psutil.Process(subproc.pid))

	dead = set()
	res = []

	def callback(proc):
		i = procs_list.index(proc)
		if not dead: # we're the first to die
			res.append(open(f"/tmp/out{i}a.bin", "rb").read())
			res.append(open(f"/tmp/out{i}b.bin", "rb").read())
		dead.add(proc)
		for other in procs_list:
			if other not in dead:
				other.kill()

	while True: 
		_, alive = psutil.wait_procs(procs_list, callback=callback)
		if not alive:
			break

	return res

if __name__ == "__main__":
	orig_prefix = b""
	prefix = orig_prefix
	blocks_a = []
	blocks_b = []
	for i in range(0x10):
		print(i)
		a, b = fastercoll(prefix)
		blocks_a.append(a)
		blocks_b.append(b)
		prefix += a

	with open("full_a.bin", "wb") as fa:
		fa.write(orig_prefix + b"".join(blocks_a))

	with open("full_b.bin", "wb") as fa:
		fa.write(orig_prefix + b"".join(blocks_b))
