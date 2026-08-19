# Quick Start

## 🚀 Start a Task

1.  Navigate to the level or scene you want to automate.
2.  Click the **"Start"** button in the program's interface.

## 💻 Command Line Arguments

You can automate startup by using command line arguments.

```bash
# Example: Automatically execute the second task (daily tasks) upon startup, and exit the program once the task completes
ok-nte.exe -t 2 -e
```

*   `-t` or `--task`: Automatically execute the N-th task upon startup. `1` represents the first task in the task list.
*   `-e` or `--exit`: Automatically exit the program after the task is completed.
