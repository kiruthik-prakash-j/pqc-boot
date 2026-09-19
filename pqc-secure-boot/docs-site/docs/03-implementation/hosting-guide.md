---
id: hosting-guide
title: Website Hosting & Server Management Guide
sidebar_label: Server Hosting Guide
---

# Website Hosting & Server Management Guide

This guide explains how to start hosting the **PQC Secure Boot Documentation** website locally and how to stop the server when needed.

---

## 1. Quick Overview

- **Access URL**: [http://localhost:3000](http://localhost:3000)
- **Directory**: `pqc-secure-boot/docs-site`

---

## 2. How to Start Hosting

Navigate to the `docs-site` directory:

```bash
cd docs-site
```

### Option A: Interactive Development Mode (Recommended)
Runs the server with hot-reloading:
```bash
npm run start
```

### Option B: Production Build & Local Preview
Compiles an optimized production build and previews it:
```bash
npm run build
npm run serve -- --port 3000 --host 0.0.0.0
```

### Option C: Background Service (Daemon Mode)
Runs the website in the background:
```bash
nohup npm run start -- --port 3000 --host 0.0.0.0 > docusaurus.log 2>&1 &
```

---

## 3. How to Stop Hosting

### Method 1: Foreground Terminal
Press **`Ctrl + C`** in the terminal where `npm run start` is active.

### Method 2: Stop by Port (Automatic)
```bash
fuser -k 3000/tcp
```

### Method 3: Stop by Process ID (Manual)
```bash
# Locate PID
lsof -i :3000

# Stop process
kill <PID>
```

### Method 4: Stop all Node Docusaurus Processes
```bash
pkill -f "docusaurus"
```
