
# Enveil

[![PyPI version](https://badge.fury.io/py/enveil.svg)](https://badge.fury.io/py/enveil)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enveil** is a secure, cross-platform Python library and CLI tool for gathering detailed system environment information, including hardware, OS, and software versions.

It is designed with security as a priority, preventing command injection by validating commands against a configurable allowlist.

## Key Features

- **Secure by Default**: Protects against command injection vulnerabilities.
- **Cross-Platform**: Works on Windows, macOS, and Linux.
- **Comprehensive Data**: Gathers details on hardware (CPU, RAM, GPU), OS (version, build, architecture), and software.
- **Flexible Output**: Provides output in human-readable format or as structured JSON, ideal for automation.
- **Extensible**: Easily define custom software version checks through a simple configuration file.
- **Dual Use**: Can be used as a standalone CLI tool or as a library in your Python projects.

## Operating Environment

Enveil is designed to run in the following environments. Administrator (root) privileges are not required for core functionality.

-   **Python Version**: `3.8` or later

-   **Operating Systems**:
    -   **Windows**: Windows 10, Windows 11, and corresponding Windows Server versions.
        -   Utilizes standard commands such as `wmic` and `nvidia-smi` (for NVIDIA GPUs).
    -   **macOS**: macOS on both Intel and Apple Silicon (M1, M2, etc.) hardware.
        -   Utilizes standard OS commands like `sysctl` and `system_profiler`.
    -   **Linux**: Major Linux distributions such as Ubuntu, Debian, CentOS, Fedora, and Arch Linux, which include standard commands (`lscpu`, `free`, `lspci`, `/etc/os-release`).

## Installation

Install Enveil from PyPI:

```bash
pip install enveil
```

## Usage as a CLI Tool

### Basic Usage

Run `enveil` to get a complete report of the system environment:

```bash
enveil
```

### Getting Specific Information

You can request specific categories of information using flags:

```bash
# Get only OS information
enveil --os

# Get hardware and software information
enveil --hardware --software
```

### JSON Output

For scripting and automation, you can get the output in JSON format:

```bash
enveil --os --hardware --format json
```

## Usage as a Library

Enveil can be easily integrated into your Python applications.

### Basic Example

```python
from enveil import EnveilAPI

# Initialize the API
api = EnveilAPI()

# Get all environment information
all_info = api.get_all_info()

# Print the results
import json
print(json.dumps(all_info, indent=2))
```

### Fetching Specific Data

You can also fetch specific categories of data. The output format is tailored for each operating system.

```python
from enveil import EnveilAPI

api = EnveilAPI()

# Get just the hardware details
hardware_info = api.get_hardware_info()
print(hardware_info)

# Get just the OS details
os_info = api.get_os_info()
print(os_info)
```

**Example Output on Windows:**
```
# hardware_info on Windows
{'CPU': 'Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz', 'RAM': '32.0GB', 'GPU': 'NVIDIA GeForce RTX 3070 (8.0GB)'}

# os_info on Windows
{'OS': 'Microsoft Windows 11 Pro', 'Version': '10.0.22631', 'Build': '22631', 'Architecture': '64-bit'}
```

**Example Output on macOS:**
```# hardware_info on macOS
{'CPU': 'Apple M2 Pro', 'RAM': '16.0GB', 'GPU': 'Apple M2 Pro (16 GB)'}

# os_info on macOS
{'OS': 'macOS', 'Version': '14.5', 'Build': '23F79'}
```

**Example Output on Linux:**
```
# hardware_info on Linux
{'CPU': 'AMD Ryzen 9 5900X 12-Core Processor', 'RAM': '62.7GB', 'GPU': 'NVIDIA GeForce RTX 3080'}

# os_info on Linux
{'OS': 'Ubuntu 22.04.3 LTS'}
```

## Configuration

Enveil checks for a list of common software by default (Python, Node.js, Docker, Git, etc.). You can fully customize this list by creating a `config.json` file.

This allows you to add your own specific tools or limit the output to only the software you care about.

**When a `config.json` file is present, it completely overrides the default software list.**

### How to Configure

1.  Create a file named `config.json` in one of the following locations:
    *   Your current working directory (where you run the `enveil` command).
    *   A system-wide configuration directory:
        *   **Linux/macOS:** `~/.config/enveil/config.json`
        *   **Windows:** `C:\Users\YourUser\AppData\Local\enveil\config.json`

2.  Define the software you want to check inside the file.

### Example: Checking for Specific Tools

If you only want to check for `Poetry` and `Git`, and ignore everything else, your `config.json` would look like this:

**Example `config.json`:**
```json
{
  "software": {
    "Poetry": {
      "command": "poetry --version"
    },
    "Git": {
      "command": "git --version"
    }
  }
}
```

### Example: Adding a Custom Tool to the Defaults

The default list is extensive, but if you want to add a tool that isn't included, you can copy the default list and add your own. For example, to add `hugo`:

**Example `config.json` to extend defaults:**
```json
{
  "software": {
    # --- Core Development Languages ---
    "Python": "python --version",
    "Python3": "python3 --version",
    "Node.js": "node -v",
    "Java": "java -version",
    "Go": "go version",
    "Rust": "cargo --version",

    # --- Language-Specific Package Managers ---
    "uv": "uv --version",
    "pip": "pip --version",
    "npm": "npm -v",
    "nvm": "nvm -v",
    "Yarn": "yarn -v",

    # --- Version Control & Containerization ---
    "Git": "git --version",
    "Docker": "docker --version",

    # --- DevOps & Cloud Infrastructure ---
    "Terraform": "terraform version",
    "kubectl": "kubectl version --client",
    "AWS CLI": "aws --version",

    # --- Your Custom Tool ---
    "Hugo": { "command": "hugo version" }
  }
}
```

By default, Enveil provides a comprehensive list of major tools. Feel free to modify your `config.json` to reduce this list if it's too extensive, add tools that are missing, or otherwise tailor it to your exact preferences.


Enveil will automatically pick up this configuration and include the specified software in its report.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.