# demo.py

# === Optimization: unused imports ===
import os
import math         # pyward: suppress  # <--- 'math' is never used, should trigger an unused-import warning
import subprocess         # <--- used below for a vulnerable subprocess call
import pickle             # <--- used below for insecure deserialization
import yaml               # <--- used below for unsafe YAML loading
import hashlib            # <--- used below for weak hashing
import python_json_logger # <--- should trigger a CVE-2025-27607 warning

# === Optimization: unused variable ===
x = 10
_unused = 5
y = 20  # <--- never used, should trigger an unused-variable warning

# === Optimization: unreachable code at module level ===
raise RuntimeError("stop here")
z = 99  # <--- unreachable

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

def optimize_patterns():
    # === Optimization: string concat in loop ===
    s = ""
    for i in range(3):
        s = s + "a"            # <--- string concatenation in loop
    print("".join([s]))

    # === Optimization: augmented add in loop ===
    t = ""
    for _ in range(2):
        t += "b"               # <--- s += … in loop

    # === Optimization: len() in loop ===
    arr = [1,2,3]
    for _ in arr:
        n = len(arr)           # <--- len() inside loop

    # === Optimization: range(len(...)) ===
    items = [10,20,30]
    for idx in range(len(items)):  # <--- range(len(...))
        print(items[idx])

    # === Optimization: list.append in loop ===
    lst = []
    for i in range(3):
        lst.append(i)         # <--- list.append in loop

    # === Optimization: list build then copy via slice ===
    temp = []
    for x in [1,2,3]:
        if x % 2 == 1:
            temp.append(x*2)
    copy = temp[:]             # <--- slice copy

    # === Optimization: dict comprehension suggestion ===
    d = {}
    for k, v in [("a",1), ("b",2)]:
        d[k] = v               # <--- dict built in loop

    # === Optimization: set comprehension suggestion ===
    s2 = set()
    for x in [1,2,3]:
        s2.add(x)              # <--- set.add in loop

    # === Optimization: generator vs list comp ===
    total = sum([x*2 for x in [1,2,3]])  # <--- sum() on list comp

    # === Optimization: membership in loop ===
    lst2 = [4,5,6]
    for val in [5,6,4]:
        if val in lst2:        # <--- membership test inside loop
            pass

def nested_loops():
    # === Optimization: complexity score (deeply nested loops) ===
    for i in range(1):
        for j in range(1):
            for k in range(1):   # <--- depth 3 exceeds default max_depth=2
                print(i, j, k)

def baz():
    # A simple function with no issues
    x = 5
    y = x * 2
    return y

if __name__ == "__main__":
    print("=== Running demo.py ===")
    try:
        foo()
    except:
        pass
    bar()
    qux()
    quux()
    corge()
    grault()
    optimize_patterns()
    nested_loops()
    print(f"baz() returns: {baz()}")
