# Lab 5 - go2web

`go2web` is a Python CLI tool that performs HTTP/HTTPS requests over raw TCP sockets and prints human-readable output.

## Features

- `go2web -h` for help
- `go2web -u <URL>` to fetch URL content over sockets
- `go2web -s <search terms...>` to search DuckDuckGo and print top 10 results
- Follows HTTP redirects (301/302/303/307/308)
- Handles HTML and JSON responses

## Requirements

- Python 3.10+
- Linux/macOS/Windows shell

## Run

```bash
chmod +x go2web
./go2web -h
./go2web -u https://example.com
./go2web -s tum web lab sockets
```

## Install as package

```bash
python3 -m pip install --user .

# if go2web is not found, add user bin to PATH
export PATH="$(python3 -m site --user-base)/bin:$PATH"

go2web -h
go2web -u https://example.com
go2web -s tum web lab sockets
```
