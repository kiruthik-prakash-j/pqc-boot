# Docusaurus Site Management Guide: Hosting & Stopping

This guide explains how to start hosting the **PQC Secure Boot Documentation** website and how to stop the running server.

---

## 1. Quick Start / Current Status

The website is configured to run on port `3000`.

- **Access URL**: [http://localhost:3000](http://localhost:3000)
- **Site Root Directory**: `docs-site`

---

## 2. How to Start Hosting

Navigate to the `docs-site` directory first:

```bash
cd docs-site
```

### Option A: Interactive Development Mode (Recommended for Editing)
Runs a local development server with hot-reloading:

```bash
npm run start
```
*To specify a custom port or external host access:*
```bash
npm run start -- --port 3000 --host 0.0.0.0
```

### Option B: Production Build & Local Preview Mode
Generates an optimized static build and serves it:

```bash
# 1. Build static production assets
npm run build

# 2. Preview the production build locally
npm run serve -- --port 3000 --host 0.0.0.0
```

### Option C: Running as a Background Service (Background / Daemon Mode)
To keep the website hosted in the background even if you close your terminal:

```bash
nohup npm run start -- --port 3000 --host 0.0.0.0 > docusaurus.log 2>&1 &
```

---

## 3. How to Stop Hosting

### Method 1: Foreground Terminal
If you ran `npm run start` or `npm run serve` directly in your active terminal:
- Press **`Ctrl + C`** to send the interrupt signal and stop the server.

### Method 2: Stop by Port (Automatic)
To terminate whatever server process is bound to port `3000`:

```bash
fuser -k 3000/tcp
```

### Method 3: Stop by Process ID (Manual PID kill)
Find the process ID (PID) listening on port `3000` or running node/docusaurus:

```bash
# Find the PID running on port 3000
lsof -i :3000

# Stop the process using its PID (replace <PID> with the actual process ID number)
kill <PID>
```
*If a graceful kill does not stop it immediately:*
```bash
kill -9 <PID>
```

### Method 4: Stop all Docusaurus / Node dev server instances
```bash
pkill -f "docusaurus"
```

---

## 4. Troubleshooting & Notes

- **`baseUrl` Warning Error**: Never open static HTML files directly via file protocol (`file:///.../index.html`) in your browser. Single Page Applications require an HTTP web server (`http://localhost:3000`) to properly map asset bundle routes.
- **Port Conflict**: If port 3000 is already in use, Docusaurus will prompt to use another port (e.g., 3001) or you can specify `--port <PORT_NUMBER>`.
