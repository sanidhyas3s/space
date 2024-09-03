# Space
A **whitespace** compiler written using `llvmlite`.

## About Whitespace
Whitespace is an esoteric programming language, where only whitespace characters (spaces " ", tabs "\t" and newlines "\n") are meaningful, all other characters can be used as comments. Read more about the syntax and semantics of the language on [Wikipedia](https://en.wikipedia.org/wiki/Whitespace_(programming_language)).

## Requirements
To run the compiler, ensure you have the following:

- Python installed (version 3.x recommended)
- `llvmlite` installed with Python

Install `llvmlite` using pip:

```bash
pip install llvmlite
```
Additionally, make sure the following tools are installed and available in your system's PATH:

- `opt` (part of LLVM)
- `llvm-dis` (part of LLVM)
- `llc` (part of LLVM)
- `g++` (GNU Compiler Collection)


## How to run?
The code files are placed in `./src` subdirectory and are run using `python` or `python3`.

To compile a whitespace file, run the following command:

```bash
python3 src/main.py <path-to-whitespace-file>
```

The sample whitespace source-codes are placed in `./samples` subdirectory. They can be compiled as specified above, for example:

```bash
python3 src/main.py samples/hello.ws
```
The compiled executables are placed in the `./exe` folder. These executables can be ran normally, for example:
```bash
cd exe
./hello
(output) Hello, world!
```

The compilation generates some temporary intermediate files in `./temp` which can be removed by running:

```bash
python3 src/main.py CLEAN
(output) 🗑 Temporary files removed.
```
---
Note: Everything except subroutines are implemented for Whitespace 0.3