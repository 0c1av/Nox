import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
	sys.path.insert(0, ROOT_DIR)

import system.starter as starter

def main():
	print("Enter target (IP or Domain): ", end="", flush=True)
	target = input()
	starter.run(target)

if __name__ == "__main__":
	main()
