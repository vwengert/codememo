# codememo
[![Build Status](https://travis-ci.com/NaleRaphael/codememo.svg?token=zhYrgBMjb73CEWtXQwny&branch=master)](https://travis-ci.com/NaleRaphael/codememo)

A note taking tool helps you trace code.

![screenshot](images/codememo_screenshot_01.png)


## Requirements
### Minimal requirements
- `imgui[pyglet] >= 1.2.0`
- `pyperclip >= 1.8.0`

    This is required for linux users only, because facilities for accessing system clipboard are not supported in the intergrated backend `pyglet` currently.

    And note that `xclip` should be installed in system (if not, you can install it by `$ sudo apt-get install xclip`).

### Use a patch for multiline input textbox
It requires to install `Cython` in order to re-compile `pyimgui`. But you don't need to install it manually, all necessary setups will be handled by `setup.py`. 
- `Cython >= 0.29.21`


## Installation
```bash
$ git clone https://github.com/naleraphael/codememo
$ cd codememo

# (recommended) install with patch
$ pip install -v --global-option="--use-forked-pyimgui" ./
# ... or install without patch
# $ pip install ./
```


## Usage
- Launch GUI
    ```bash
    $ python -m codememo
    ```


## Note
- This project is still under development, but please feel free to use it and give us feedback. ;)
- Configuration files and crash dump files will be stored under the folder `$HOME/.codememo`.