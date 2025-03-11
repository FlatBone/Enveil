# Enveil
A cross-platform utility for gathering detailed system information including hardware specifications, OS details, and software versions.

## Features

- **Cross-Platform Support**: Works on Windows, macOS, and Linux
- **Comprehensive Information Collection**:
  - Hardware: CPU, RAM, and GPU details
  - Operating System: Version, edition, and build information
  - Software: Version information for user-specified applications
- **Flexible Usage**:
  - Interactive mode with prompts
  - Command-line arguments for scripted operations
- **Customizable**: Configure additional software to check via config.json

## Requirements

- Python 3.6 or higher
- Operating system-specific dependencies are handled automatically

## Installation

1. Clone this repository or download the script:
   ```
   git clone https://github.com/yourusername/environment-info-tool.git
   ```
   
2. Navigate to the directory:
   ```
   cd environment-info-tool
   ```

3. No additional installation steps are required - the script uses standard libraries.

## Usage

### Interactive Mode

Run the script without arguments to use interactive mode:

```
python env_info.py
```

You'll be prompted to select what information you want to retrieve:
- Hardware information
- OS information
- Software versions

### Command-line Arguments

For automated use, you can specify what information to collect using arguments:

```
python env_info.py --hardware --os --software
```

To check specific software versions:

```
python env_info.py --software=Python,Git,Docker
```

### Configuration

Create a `config.json` file in the same directory as the script to define custom software checks:

```json
{
  "software": {
    "Python": "python --version || python3 --version",
    "Node.js": "node -v",
    "npm": "npm -v",
    "MyCustomTool": "mycustomtool --version"
  }
}
```

## Example Output

```
=== Result ===
CPU: Intel(R) Core(TM) i7-10700K CPU @ 3.80GHz
RAM: 32.0GB
GPU: NVIDIA GeForce RTX 3070 (8.0GB)
OS: Windows 11 Pro 21H2
Python: Python 3.9.7
Docker: Docker version 20.10.17, build 100c701
Git: git version 2.37.1.windows.1
```

## Troubleshooting

If you encounter any issues:

- Ensure you have proper permissions to execute system commands
- On Linux/macOS, some hardware information may require root/sudo access
- For GPU information on Linux, ensure appropriate drivers are installed

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.