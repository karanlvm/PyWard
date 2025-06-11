# triggers check_weak_hashing_usage
import hashlib

h1 = hashlib.md5(b"hello").hexdigest()
h2 = hashlib.sha1(b"world").hexdigest()
