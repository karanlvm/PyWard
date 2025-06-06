# demo.py

# === Optimization: unused imports ===
import os
import math               # <--- 'math' is never used, should trigger an unused-import warning
import subprocess         # <--- used below for a vulnerable subprocess call
import pickle             # <--- used below for insecure deserialization
import yaml               # <--- used below for unsafe YAML loading
import hashlib            # <--- used below for weak hashing
import python_json_logger # <--- should trigger a CVE-2025-27607 warning

# === Security: hard-coded secrets (should trigger hardcoded-secret warnings) ===
API_KEY = "ABCD1234"              # <--- hard-coded secret
DB_PASSWORD = "hunter2"           # <--- hard-coded secret

def foo():
    print("Inside foo(): this will print.")
    return
    # Everything below this return is unreachable:
    print("This line is unreachable and should trigger an unreachable-code warning.")
    x = 42
    print(f"This {x} will also never run.")

def bar():
    # === Security: eval and exec usage ===
    result = eval("3 * 7")       # <--- should trigger an eval warning (CVE-2025-3248)
    print(f"Result of eval: {result}")

    exec("print('Running exec-generated code!')")  # <--- should trigger an exec warning

def qux():
    # === Security: subprocess with shell=True (should trigger a shell-injection warning) ===
    cmd = "ls -la /"
    subprocess.run(cmd, shell=True)
    # Unreachable code after a return
    return
    subprocess.run("whoami", shell=True)

def quux():
    # === Security: insecure pickle usage ===
    try:
        with open("data.pickle", "rb") as f:
            data = pickle.load(f)   # <--- should trigger a pickle.load warning
            print(f"Unpickled data: {data}")
    except FileNotFoundError:
        print("No pickle file found.")

def corge():
    # === Security: unsafe YAML loading ===
    try:
        with open("config.yaml", "r") as f:
            cfg = yaml.load(f)      # <--- should trigger a yaml.load without SafeLoader warning
            print(f"Loaded YAML: {cfg}")
    except FileNotFoundError:
        print("No YAML config found.")

def grault():
    # === Security: weak hashing usage (should trigger weak-hash warnings) ===
    data = b"secret data"
    h1 = hashlib.md5(data, usedforsecurity=True)    # <--- should trigger hashlib.md5 warning
    h2 = hashlib.sha1(data)   # <--- should trigger hashlib.sha1 warning
    h3 = hashlib.sha256(data) # <--- this is okay
    print(f"MD5: {h1.hexdigest()}")
    print(f"SHA1: {h2.hexdigest()}")
    print(f"SHA256: {h3.hexdigest()}")

def baz():
    # A simple function with no issues
    x = 5
    y = x * 2
    return y

if __name__ == "__main__":
    print("=== Running demo.py ===")
    foo()
    bar()
    qux()
    quux()
    corge()
    grault()
    print(f"baz() returns: {baz()}")
