

import sys

def main():
    if len(sys.argv) > 1:  # Check if any arguments were passed
        print("Parameter given in command line:", sys.argv[1])
    else:
        print("No parameter was provided.")

if __name__ == "__main__":
    main()
