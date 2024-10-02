import sys

import hashlib
from pathlib import Path

import httpx


CHANNEL_NAME = "anemo"
channel: str = f"https://prefix.dev/api/v1/upload/{CHANNEL_NAME}"


def upload(fn, token: str):
    data = fn.read_bytes()

    # if larger than 100mb, skip
    if len(data) > 100 * 1024 * 1024:
        print("Skipping", fn, "because it is too large")
        return

    name = fn.name
    sha256 = hashlib.sha256(data).hexdigest()
    headers = {
        "X-File-Name": name,
        "X-File-SHA256": sha256,
        "Authorization": f"Bearer {token}",
        #"Content-Length": str(len(data) + 1),
        "Content-Type": "application/octet-stream",
    }

    print("Uploading conda package...")
    r = httpx.post(
        url=channel,
        data=data,
        headers=headers,
        timeout=None,  # 30 seconds timeout
    )

    print(f"Uploaded package {name} with status {r.status_code}")

 
if __name__ == "__main__":
    if len(sys.argv) > 2:
        # print(f"Package: {sys.argv[1]}")
        # print(f"Token: {sys.argv[2]}")

        package = Path(sys.argv[1])  # get path
        token: str = sys.argv[2]
        upload(package, token)
    else:
        print("Usage: upload-prefixdev.py <package> <token>")
        sys.exit(1)
