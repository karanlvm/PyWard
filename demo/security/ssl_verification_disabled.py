# triggers check_ssl_verification_disabled
import requests

requests.get("https://example.com", verify=False)
session = requests.Session()
session.post("https://api.example.com", verify=False)
