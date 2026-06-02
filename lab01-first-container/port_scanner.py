# Port Scanner
import argparse
import socket
import json


def check_port(host, port):
    s = socket.socket()  # creates a socket, like opening a "phone line"
    s.settimeout(1)  # waits a maximum of 1 second for a response

    result = s.connect_ex((host, port))  # tries to connect
    s.close()  # closes the line

    return result == 0  # 0 = connected = open port, other number = closed


def scan(host, start_port, end_port):
    results = []

    for port in range(start_port, end_port + 1):
        # this if is true in the conditional 
        if check_port(host, port):  # if check_port(host, port) == True:
            structure = {
                "port": port,
                "status": "Open"
            }
            results.append(structure)
    return results


def save_json(result, filename="result.json"):
    # uses json.dump to save results into a file
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Port Scanner")
    parser.add_argument("--host", required=True)
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=1024)
    args = parser.parse_args()
    
    print(f"Scanning {args.host}...")  # <-- args.host = google.com
    results = scan(args.host, args.start, args.end)
    save_json(results)
    print(f"Results saved in 'result.json'")


if __name__ == '__main__':
    main()
