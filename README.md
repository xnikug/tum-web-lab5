# Lab 5 - go2web

`go2web` is a Python CLI tool that performs HTTP/HTTPS requests over raw TCP sockets and prints human-readable output.

## Features

- `go2web -h` for help
- `go2web -u <URL>` to fetch URL content over sockets
- `go2web -s <search terms...>` to search DuckDuckGo and print top 10 results
- Follows HTTP redirects (301/302/303/307/308)
- Handles HTML and JSON responses (content negotiation)
- Supports HTTP cache (repeated requests can be served from cache)

## Project Structure
- `go2web_cli.py`  
  Thin CLI wrapper/entrypoint.
- `go2web_app/cli.py`  
  Argument parsing and command routing (`-h`, `-u`, `-s`).
- `go2web_app/commands.py`  
  Implements URL mode and search mode logic.
- `go2web_app/http_client.py`  
  Raw socket + SSL HTTP client:
  - builds HTTP requests manually,
  - sends over TCP,
  - parses status/headers/body,
  - handles redirects,
  - integrates cache logic (if enabled in your implementation).
- `go2web_app/parsers.py`  
  HTML parsing for search results.
- `go2web_app/formatters.py`  
  Human-readable rendering/decoding for HTML/JSON/text.
- `go2web_app/models.py`  
  Shared response/data models.

## Requirements

- Python 3.10+
- Linux/macOS/Windows shell

## Run (script mode)

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

## Testing Examples

### 1) Help command
```bash
go2web -h
```
Expected: usage info with `-h`, `-u`, `-s`.

### 2) URL fetch over raw sockets
```bash
go2web -u https://example.com
```
Expected: HTTP status + readable text output (without raw HTML noise).

### 3) Search mode (top 10)
```bash
go2web -s tcp sockets python tutorial
```
Expected: top results with direct links.

### 4) Redirect handling test
```bash
go2web -u http://example.com
```
Expected: redirect followed automatically to HTTPS endpoint.

### 5) JSON handling test
```bash
go2web -u https://httpbin.org/json
```
Expected: pretty-printed JSON output.

### 6) Cache test
```bash
go2web -u https://example.com
go2web -u https://example.com
```
Expected: second call uses cached response (faster and/or cache-hit indication depending on current output settings).

