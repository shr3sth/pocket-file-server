# 📱 Pocket File Server

A lightweight HTTP file server built with Python and Flask, running directly on an Android phone through Termux. It allows another device on the same local network to browse, download, and stream files through a web browser.

The project explores practical networking, HTTP, authentication, file serving, and basic security testing using everyday hardware.

## Features

* **HTTP file sharing:** Browse directories and access files from a web browser.
* **Authentication:** HTTP Basic authentication with a username and password.
* **Media streaming:** Stream supported audio and video files through the browser.
* **Server monitoring:** View uptime, HTTP request count, and storage information.
* **Directory traversal protection:** Resolve requested paths and restrict access to the configured shared directory.
* **Lightweight interface:** A responsive file browser and monitoring dashboard.
* **Android-based hosting:** Runs on an Android phone using Termux.

## Architecture

Android phone (Termux + Python + Flask)
↓ HTTP over local Wi-Fi/hotspot
Laptop or another client device (web browser)

## Requirements

* Android phone with Termux
* Python 3
* Flask
* A local Wi-Fi network or personal hotspot
* A client device with a web browser

## Setup

Install the required packages in Termux:

```bash
pkg update
pkg install python
python -m pip install flask
termux-setup-storage
```

Place the server script at `~/bin/sd-server-v2.py` and configure the shared directory in the script to match your storage location.

Start the server:

```bash
python ~/bin/sd-server-v2.py
```

Enter the server password when prompted. Open the displayed phone IP address and port in a browser on a device connected to the same network.

Example:

```text
http://PHONE-IP:8000
```

The phone's IP address may change when the hotspot reconnects.

## Security and limitations

* Intended for trusted local networks and demonstrations.
* HTTP traffic is unencrypted; Basic authentication does not encrypt credentials.
* Anyone who can reach the server may attempt to connect, so authentication must remain enabled.
* Only the configured shared directory should be exposed.
* The Flask development server is intended for this small demonstration, not production deployment.
* Do not expose the server directly to the public internet.

## Testing

The following checks were performed:

* Unauthenticated request returned HTTP 401.
* Authenticated request returned HTTP 200.
* A directory traversal attempt was rejected with HTTP 403.
* File browsing, downloads, media streaming, and the monitoring dashboard were tested.

## Future improvements

Possible future work includes HTTPS or SSH tunnelling, more detailed request logging, and improved server lifecycle management.

## Author

Shresth Dehuliya

Built as a hands-on project to explore Python, Linux command-line tools, HTTP, and practical networking.
