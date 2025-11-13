# Vultr Mobile Client

An Android application for managing Vultr cloud services.

## Features

- **Mobile-First UI**: Kivy-based mobile application optimized for Android
- **Full API Integration**: Complete integration with Vultr API v2
- **Instance Management**: Create, delete, start, stop, and reboot instances from your mobile device
- **Resource Browser**: View and select regions, plans, and OS images
- **Real-time Status**: Monitor instance status and IP addresses
- **Secure**: API key authentication with secure storage

## Project Structure

```
vultrApp/
├── src/vultr_cli/          # Main package
│   ├── api/                # API client module
│   │   ├── __init__.py
│   │   └── client.py       # VultrAPI client class
│   ├── ui/                 # UI module
│   │   ├── __init__.py
│   │   └── app.py          # Kivy app implementation
│   ├── utils/              # Utility functions
│   │   └── __init__.py
│   └── __init__.py
├── docs/                   # Documentation
├── main.py                 # Android app entry point
├── pyproject.toml          # Project configuration
├── buildozer.spec          # Android build configuration
└── openapi.json           # Vultr API specification
```

## Installation & Building

### Prerequisites

```bash
# Install buildozer
pip install buildozer

# Install Cython (required for Kivy)
pip install cython
```

### Build Android APK

```bash
# Build debug APK
buildozer android debug

# Build release APK
buildozer android release

# Build and automatically deploy to connected device
buildozer android debug deploy run
```

### Install on Device

```bash
# Deploy to connected Android device
buildozer android deploy run

# Or manually install the APK
adb install bin/vultrcli-1.0.0-arm64-v8a-debug.apk
```

## Usage

### First Launch

1. Install the APK on your Android device
2. Open the app
3. Enter your Vultr API key when prompted
4. The app will verify the API key and load the main interface

### Main Features

#### Deploy New Instance
- Tap "Deploy" in the navigation
- Select Region (data center location)
- Choose Plan (server specifications)
- Select Operating System
- Enter a label for your instance
- Tap "Deploy Instance"

#### Manage Instances
- Tap "Instances" in the navigation
- View all your instances with status and IP information
- Start, Stop, Reboot, or Delete instances
- Pull-to-refresh to update instance status

#### API Key Management
- API key is stored securely for the session
- You can re-enter API key from the app if needed
- No API key is stored permanently on the device

## Configuration

### Build Configuration

Edit `buildozer.spec` to customize:
- App version: `version = 1.0.0`
- Package name: `package.name = vultrcli`
- App title: `title = Vultr CLI`
- Target architecture: `android.archs = arm64-v8a`

### Android Requirements

- Minimum Android API: 21 (Android 5.0)
- Target Android API: 34 (Android 14)
- Architecture: arm64-v8a (modern 64-bit devices)
- Permissions: INTERNET (for API communication)

## Development

### Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# For development with additional tools
pip install -e ".[dev]"
```

### Code Quality

```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

## Dependencies

### Core Dependencies
- `kivy>=2.1.0` - GUI framework for mobile app
- `requests>=2.31.0` - HTTP client for API calls
- `certifi>=2023.7.22` - SSL certificates
- `urllib3>=1.26.18` - HTTP library
- `charset-normalizer>=3.3.0` - Character encoding detection
- `idna>=3.4` - Internationalized domain names
- `cython` - Required for Kivy on Android

### Development Dependencies
- `black>=22.0.0` - Code formatting
- `flake8>=5.0.0` - Linting
- `mypy>=1.0.0` - Type checking
- `pre-commit>=2.20.0` - Git hooks

### Android Build Dependencies
- `buildozer>=1.5.0` - Android build tool
- `python-for-android>=2023.0.0` - Python Android support

## API Integration

### VultrAPI Client

The app uses `VultrAPI` class to interact with Vultr API:

- `get_plans(plan_type="vc2")` - Get available server plans
- `get_regions()` - Get available data center regions
- `get_os_images()` - Get available operating systems
- `create_instance(config)` - Create a new instance
- `get_instances()` - List all instances
- `get_instance(instance_id)` - Get specific instance details
- `delete_instance(instance_id)` - Delete an instance
- `start_instance(instance_id)` - Start a stopped instance
- `stop_instance(instance_id)` - Stop a running instance
- `reboot_instance(instance_id)` - Reboot an instance

## Troubleshooting

### Build Issues

- **Cython errors**: Make sure Cython is installed: `pip install cython`
- **NDK download errors**: Check your internet connection and Android SDK settings
- **Architecture issues**: Only arm64-v8a is configured in buildozer.spec
- **jnius compilation errors**: When encountering Cython compilation errors related to jnius, you may need to manually modify the following .pyx files:
  - `.buildozer/android/platform/build-arm64-v8a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/`
    - `jnius_conversion.pxi`
    - `jnius_utils.pxi`
    - `jnius.pyx`
  - `.buildozer/android/platform/build-arm64-v8a/build/other_builds/kivy/arm64-v8a__ndk_target_21/kivy/kivy/`
    - `weakproxy.pyx`
    - `graphics/opengl.pyx`
    - `graphics/context_instructions.pyx`
  These modifications are typically needed to fix Cython syntax compatibility issues with newer Python versions or Android NDK targets.

### Runtime Issues

- **API errors**: Verify your API key is valid and has appropriate permissions
- **Network errors**: Ensure the app has internet permission and device is online
- **SSL errors**: The app includes certifi for SSL certificate verification

## License

MIT License - see LICENSE file for details.

Copyright (c) 2025 LNOVICE

## Support

For issues and questions:
- Create an issue on GitHub
- Review the Vultr API documentation
- Check buildozer and python-for-android documentation for build issues
