# Swerve
## Installing the Swerve Compiler
1. Acquire a computer running windows.
2. Download this repository onto your computer in a place where it is easy to access.
3. If you haven't already installed a copy, install the MSVC redistributable, which can be found
[here](https://docs.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170).
4. Install Python 3.10 (the version is necessary). When prompted, you should probably select the 
option to add Python to your path, as that makes using Python much easier.
5. Using pip, install the Python library llvmlite. Make sure your pip is for your Python 3.10
install.
6. In command prompt, change your current working directory to the one containing the 
`swerve` directory.
7. You can now run the compiler using a command like `python -m swerve <path-to-input-file> -o<path-to-output-file>`.