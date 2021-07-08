# PyBack v1.1

PyBack is a really simple script written in python that allows you to remote a computer via reverse tcp.



## Installation

Use git clone to install it:
```bash
git clone https://github.com/Omikrone/PyBack.git
```
Or install it manually.


## Requirements

If you want to create executables for Windows, use pip and install te requirements:
```bash
pip3 install -r requirements.txt
```

**Troubleshot:** It may be possible that when you install PyInstaller you can't launch it. In this case, you have to install [the wheel file](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyinstaller) manually and then run:
```bash
pip3 install PyInstaller‑3.6‑py2.py3‑none‑any.whl
```


## Usage and Set Up

Change directory and launch pyback.py:
```bash
cd PyBack
python3 pyback.py
```
You can then set up the client and the listener with the differents options.


## Remote control

There is for the moment 3 main commands available:
``` bash
- upload : upload a file to the client.
- download : download a file from the client.
- cmd : open an interactive shell on the client's machine.
```

Use 'help' to see the commands and 'exit' to leave the session.


## Disclaimer and further information

This program is for educational purposes only! I take no responsibility or liability for own personal use.

Inspired by: [Oseid on GitHub](https://github.com/Oseid/python-reverse-shell)
