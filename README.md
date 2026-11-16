# FileDrop

<p align="center">
  **Share files. Instantly. Anywhere.**
</p>

<p align="center">
  A free and open-source file-sharing application built with Python.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Open%20Source-Yes-success?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" />
</p>

---

## About

**FileDrop** is a simple file-sharing application that allows users to share files between devices through a unique transfer code and QR code.

No account. No complicated setup. Just select, share and download.

Our goal is to make file sharing accessible, fast and free for everyone.

## Features

- 📁 **Easy file sharing** — Upload and share files through a simple interface.
- 📱 **QR Code sharing** — Scan a QR code to join a transfer.
- 🔢 **Unique transfer codes** — Join transfers using a six-character code.
- 🌐 **Multi-device support** — Access FileDrop from different devices using a web browser.
- 🔓 **No account required** — Start sharing without registration.
- 🆓 **Free and open source** — Available for everyone.

## Preview

The FileDrop interface features a minimalist dark design with a modern blue and purple visual identity.

## Installation

### Requirements

- Python 3.10 or newer
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/FileDrop.git
cd FileDrop
```

### 2. Install dependencies

```bash
pip install aiohttp "qrcode[pil]"
```

### 3. Run FileDrop

```bash
python filedrop.py
```

### 4. Open the application

Visit:

```text
http://localhost:8000
```

To access FileDrop from another device on the same local network, use the network address displayed in your terminal.

## How to use

1. Open FileDrop in your browser.
2. Select the files you want to share.
3. Click **Create transfer**.
4. Share the generated QR code or transfer code.
5. Open FileDrop on another device.
6. Enter the transfer code.
7. Download your files.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend |
| aiohttp | HTTP server |
| HTML & CSS | User interface |
| JavaScript | Frontend interactions |
| QRCode | QR code generation |

## Current limitations

FileDrop is currently an early prototype.

- Files are temporarily stored in server memory.
- Maximum file size: 100 MB per file.
- Transfers currently require access to the same server.
- QR code access currently uses a local network address.
- Files are not yet transferred directly between devices.
- No end-to-end encryption is implemented yet.

**Important:** Do not use the current prototype to transfer sensitive or confidential files.

## Roadmap

Our long-term vision for FileDrop:

- [x] Basic file upload and download
- [x] Unique transfer codes
- [x] QR code generation
- [x] Modern web interface
- [ ] WebRTC direct device-to-device transfers
- [ ] End-to-end encryption
- [ ] Drag and drop improvements
- [ ] Transfer progress and speed indicators
- [ ] Mobile interface improvements
- [ ] Multiple simultaneous transfers
- [ ] Public deployment support

## Contributing

Contributions are welcome!

If you have ideas, find bugs or want to improve FileDrop:

1. Fork this repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License

FileDrop is released under the **MIT License**.

See the `LICENSE` file for more information.

---

<p align="center">
  **FileDrop**
  <br>
  Share files. Instantly. Anywhere.
  <br><br>
  Made with ❤️ for everyone.
</p>

https://github.com/user-attachments/assets/6c0b7f2c-3b19-4f8a-8a23-019aaeb0f8d2


