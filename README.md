# Pocket File Server (Termux)

A small Flask HTTP file server for Android/Termux. It provides authenticated directory browsing, file downloads, browser-based media access, and a basic status panel.

## Files

- `sd-server.py` — server application.
- `pocket-server` — one-command launcher.
- `install.sh` — installs Flask and copies the server and launcher to `~/bin`.
- `requirements.txt` — Python dependency list.

## Install on the Android phone

1. Extract this ZIP on the phone.
2. Open Termux and navigate to the extracted folder.
3. Grant Termux storage access if you have not already:

   ```bash
   termux-setup-storage
   ```

4. Install Python if needed:

   ```bash
   pkg update
   pkg install python
   ```

5. Run the installer from the extracted folder:

   ```bash
   bash install.sh
   ```

The default shared directory is `/storage/sdcard1`, matching a secondary SD card on some devices. If your SD card uses a different path, set `SD_SERVER_ROOT` before starting the server, for example:

```bash
SD_SERVER_ROOT=/storage/your-card-path ~/bin/pocket-server
```

## Start and stop

Start:

```bash
~/bin/pocket-server
```

Enter a username and password when prompted. The password is not stored in this project.

Stop the server with `Ctrl+C`.

The server listens on port `8000` by default. If needed, you can choose another port:

```bash
SD_SERVER_PORT=8080 ~/bin/pocket-server
```

Open `http://PHONE-IP:8000` (or the selected port) from a browser on a device connected to the same trusted Wi-Fi/hotspot. Find the phone's current IP address in Android hotspot or network details; it may change after reconnecting.

## Security notes

- This project is intended for learning and trusted local-network demonstrations.
- HTTP is **not encrypted**. Basic authentication does not protect credentials or file contents from network eavesdropping.
- Keep authentication enabled and do not configure router port forwarding or expose this server to the public internet.
- The server shares the configured root directory and its accessible contents. Do not use it while sensitive files are in the shared directory.
- Flask's built-in development server is used for this small demo; it is not intended as a production deployment.

## Tested behavior

The project was tested with `curl`:
- Unauthenticated request: HTTP `401`.
- Authenticated request: HTTP `200`.
- Directory traversal attempt: HTTP `403`.

File browsing, downloads, media access, and the status panel were also tested in the project environment.

## Architecture

Android phone (Termux + Python + Flask)  
→ HTTP over local Wi-Fi/hotspot  
→ Laptop or another client browser
