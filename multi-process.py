import subprocess
import sys


def run_command(command, processes):
    # run the processes and print their outputs
    processes = [subprocess.Popen(command, shell=True) for _ in range(processes)]
    for process in processes:
        process.wait()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: multi-process.py <processes> <command>")
        sys.exit(1)
    run_command(" ".join(sys.argv[2:]), int(sys.argv[1]))
