import sys
from datetime import datetime

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python3 auto_apply.py <pdf file>")
        sys.exit(1)
    print(f"analysing cv '{sys.argv[1]}'")
    timestamp = datetime.now().isoformat()
    with open("test_log.log", "w") as f:
        f.write(f"[{timestamp}] hello world {sys.argv[1]}")
