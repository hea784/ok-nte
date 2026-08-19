# Installation

## 🖥️ System Requirements & Compatibility

*   **Operating System**: Windows
*   **Game Resolution**: 1920x1080 or higher (**16:9 aspect ratio only**)
*   **Game Language**: Simplified Chinese / English

## 🚀 Installation Guide

### Method 1: Using the Installer (Recommended)

This method is suitable for most users. It's simple, fast, and supports automatic updates.

1.  Go to the [**Releases**](https://github.com/BnanZ0/ok-nte/releases) page.
2.  Download the latest `ok-nte-win32-Global-setup.exe` file.
3.  Double-click the installer and follow the prompts to complete the installation.

### Method 2: Running from Source (For Developers)

This method requires a Python environment and is suitable for users who want to contribute, modify, or debug the code.

1.  **Prerequisites**: Ensure you have **Python 3.12** installed.
2.  **Clone the repository**:
    ```bash
    git clone https://github.com/BnanZ0/ok-nte.git
    cd ok-nte
    ```
3.  **Install dependencies**:
    ```bash
    uv sync
    # or
    pip install -r requirements.txt
    ```

    **💡 Tip**: After pulling new code, it's recommended to run this command again to ensure all dependencies are up to date.
4.  **Run the application**:
    ```bash
    # Run the standard version
    python main.py

    # Run the debug version (outputs more detailed logs)
    python main_debug.py
    ```
