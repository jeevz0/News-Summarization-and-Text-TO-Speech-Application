import os
client_file = '/usr/local/lib/python3.10/site-packages/googletrans/client.py'

# Only patch if needed
if os.path.exists(client_file):
    with open(client_file, 'r') as file:
        content = file.read()

    patched = content.replace(
        "proxies: typing.Dict[str, httpcore.SyncHTTPTransport] = None,",
        "proxies = None,"
    )

    with open(client_file, 'w') as file:
        file.write(patched)

    print("✅ googletrans patch applied.")
else:
    print("❌ client.py not found.")
