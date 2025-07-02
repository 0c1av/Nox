import system.starter as starter
if __name__ == "__main__":
	print("Enter target (IP or Domain): ", end="", flush=True)
	target = input()
	starter.run(target)
