# Print Queue Reset

Windows tool that pauses printing, clears the print queue, and resumes printing.

It stops the Print Spooler service, deletes the spool files in the print buffer, and starts the service again. Documents that have not been printed are removed from the queue.

The window is available in Polish, Swedish, and English. It follows the Windows display language. In the Python version you can override that with `--lang pl`, `--lang sv`, or `--lang en`, or with the `PQR_LANG` environment variable set to `pl`, `sv`, or `en`.

There are two builds of the same tool: a Python/tkinter app and a small C/Win32 executable.

## Requirements

- Windows 10 or Windows 11
- Administrator rights. Stopping the Print Spooler service and deleting spool files need elevation. The program asks through UAC. If you cancel the prompt, the window still opens and shows a button to run as administrator.

## Run the Python version

Python 3 with the standard library is enough, including tkinter. No third-party packages are required.

```bat
python run.py
```

## Build the native version

The `native/` directory is the C/Win32 program. It does not need Python at runtime.

On Windows, from `native/`:

```bat
build.bat
```

The script uses GCC (MinGW / WinLibs). If GCC is not on `PATH`, it falls back to TCC at `tools\tcc\tcc\tcc.exe`. The executable is written to `portable\PrintQueueReset.exe`.

## Build a standalone Python executable

From the repository root, on Windows, with PyInstaller installed:

```bat
build.bat
```

That produces `portable\PrintQueueReset.exe` and copies `CZYTAJ.txt`, `LICENSE`, and `NOTICE` into `portable/`. The native build writes the same file name, so run only the build you want to ship.

## License

MIT License. Copyright (c) 2026 Tomasz Mucha. See [LICENSE](LICENSE).
