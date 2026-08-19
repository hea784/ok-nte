# FAQ and feedback

## FAQ

<details>
<summary><strong>What should I do if the update is stuck?</strong></summary>

If the ok-nte update shows no progress for a long time, the dependency download may be too slow. Try the following solutions:

1. Open Settings in the upper-right corner of the console and switch to a pip mirror with a faster download speed.
2. Enable a jump host or proxy, then use the official PyPI source to update again.
3. Uninstall the current version of ok-nte, then download the latest setup installer through an official channel and install it again.

</details>

<details>
<summary><strong>Recognition or clicks are unstable</strong></summary>

Check the following in order:

1. The resolution is 16:9 and at least 1920×1080.
2. The game brightness, UI opacity, and keybindings use the recommended settings.
3. Graphics filters, HDR, sharpening, and screen overlays are disabled.
4. The game window is not minimized, and the screen is not locked or asleep.
5. The mouse is not interfering with the foreground game window while the task is running.

</details>

<details>
<summary><strong>Installation or startup fails</strong></summary>

- Confirm that you are using the latest installer, and add the installation directory to your security software's trusted list if it blocks application files.
- When running from source, run `uv sync` again to install project-compatible dependencies.
- Do not run the application from a directory with unusual permission restrictions; move it to a directory writable by the current user if necessary.

</details>

<details>
<summary><strong>Audio trigger does not respond</strong></summary>

The audio trigger uses Windows WASAPI per-process loopback to read output audio directly from the target game process and its child processes; it does not depend on the system default output device.

If it does not trigger, check the following:

- The game process is running and the game is actually producing audio.
- The audio-trigger feature is enabled and configured correctly in the application.
- The current Windows environment supports per-process loopback capture.

</details>

## Bug Reports & Feedback

If the solutions above do not resolve your issue, feel free to report it via [**Issues**](https://github.com/BnanZ0/ok-nte/issues). To help us quickly identify the problem, please provide the following information in your report:

- **Screenshot**: A clear image of the error or unusual behavior.
- **Log File**: Attach the `.log` file from the program's directory.
- **Detailed Description**: What were you doing? What exactly happened? Can you reproduce the issue consistently, or does it happen randomly?
