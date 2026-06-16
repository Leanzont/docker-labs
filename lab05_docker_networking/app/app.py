import urllib.request

url = "http://nginx-server"

try:
    response = urllib.request.urlopen(url)
    print(f"Connected to {url}")
    print(f"Status: {response.status}")
    print(f"Response: {response.read(100).decode()}")
except Exception as e:
    print(f"Failed to connect: {e}")
