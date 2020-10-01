ISIMIP quality control
======================

[![Python Version](https://img.shields.io/badge/python-3.7|3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/ISI-MIP/isimip-qc/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/ISI-MIP/isimip-qc.svg?branch=master)](https://travis-ci.org/ISI-MIP/isimip-qc)
[![Coverage Status](https://coveralls.io/repos/github/ISI-MIP/isimip-qc/badge.svg?branch=master)](https://coveralls.io/github/ISI-MIP/isimip-qc?branch=master)

A command line tool for the quality control of climate impact data of the ISIMIP project. It mainly covers tests of:
- the file name against the protocol schemas and patterns
- variables, dimensions and global attributes
- data model and types
- some consistency checks on the NetCDF time axis and
- if the data is within a valid value range (when defined in the ISIMIP protocol)

**This is still work in progress.**


Prerequisites
-------------

The application is written in Python (> 3.6) uses only dependencies, which can be installed without administrator priviledges. The installation of Python (and its developing packages), however differs from operating system to operating system. Optional Git is needed if the application is installed directly from GitHub.

### Linux

On Linux, Python3 is probably already installed, but the development packages are usually not. You should be able to install them using:

```
# Ubuntu/Debian
sudo apt-get install python3 python3-dev python3-venv

# CentOS/RHEL
sudo yum install python3 python3-devel

# openSUSE/SLES
zypper install python3 python3-devel
```

Git can be installed in a similar way using the `git` package (on all distributions).

### macOS

While we reccoment using [Homebrew](https://brew.sh) to install Python3 on a Mac, other means of obtaining Python like [Anaconda](https://www.anaconda.com/products/individual), [MacPorts](https://www.macports.org/), or [Fink](https://www.finkproject.org/) should work just as fine:

```
brew install python
brew install git
```

### Windows

#### Regular installation

The software prerequisites need to be downloaded and installed from their particular web sites.

For python:
* download from <https://www.python.org/downloads/windows/>
* use the 64bit version if your system is not very old
* **don't forget to check 'Add Python to PATH' during setup**

For git:
* download from <https://git-for-windows.github.io/>
* use the 64bit version if your system is not very old

All further steps need to be performed using the windows shell `cmd.exe`. You can open it from the Start-Menu.

#### Using the Windows Subsystem for Linux (WSL)

As an alternative for advanced users, you can use the Windows Subsystem for Linux (WSL) to install a Linux distribution whithin Windows 10. The installation is explained in the [Microsoft documentation](https://docs.microsoft.com/en-us/windows/wsl/install-win10). When using WSL, please install Python3 as explained in the Linux section.

Setup
-----

The tool can be installed via pip. Usually you want to create a [virtual environment]() first, but this is optional.

```bash
# setup venv on Linux/macOS/Windows WSL
python3 -m venv env
source env/bin/activate

# setup venv on Windows cmd
python -m venv env
call env\Scripts\activate.bat

# install from GitHub
pip install git+https://github.com/ISI-MIP/isimip-qc

# update from Github
pip install --upgrade git+https://github.com/ISI-MIP/isimip-qc
```

Usage
-----

The tool has several options which can be inspected using the help option `-h, --help`:

```plain
usage: isimip-qc [-h] [--config-file CONFIG_FILE] [-c] [-m] [--unchecked-path UNCHECKED_PATH] [--checked-path CHECKED_PATH] [--protocol-location PROTOCOL_LOCATIONS] [--log-level LOG_LEVEL] [--log-path LOG_PATH] [-f] [-w] [-e]
                 [-r [MINMAX]] [--fix] [--fix-datamodel [FIX_DATAMODEL]] [--check CHECK]
                 schema_path

Check ISIMIP files for matching protocol definitions

positional arguments:
  schema_path           ISIMIP schema_path, e.g. ISIMIP3a/OutputData/water_global

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        File path of the config file
  -c, --copy            Copy checked files to CHECKED_PATH if now warnings or errors were found
  -m, --move            Move checked files to CHECKED_PATH if now warnings or errors were found
  --unchecked-path UNCHECKED_PATH
                        base path of the unchecked files
  --checked-path CHECKED_PATH
                        base path for the checked files
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol when different from official repository
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-path LOG_PATH   base path for the individual log files
  -f, --first-file      only process first file found in UNCHECKED_PATH
  -w, --stop-on-warnings
                        stop execution on warnings
  -e, --stop-on-errors  stop execution on errors
  -r [MINMAX], --minmax [MINMAX]
                        test values for valid range (slow, argument MINMAX defaults to show the top 10 values)
  --fix                 try to fix warnings detected on the original files
  --fix-datamodel [FIX_DATAMODEL]
                        also fix warnings on data model found using NCCOPY or CDO (slow). Choose preferred tool per lower case argument.
  --check CHECK         perform only one particular check
```

The only mandatory argument is the `schema_path`, which specifies the pattern and schema to use. The `schema_path` consitst of the `simulation_round`, the `product`, and the `sector` seperated by slashes, e.g. `ISIMIP3a/OutputData/water_global`.

### The options in detail

* `--config-file`: Default values for the optional arguments are set in the code, but can also be provided via:
    * a config file given by `--config-file`, or located at `isimip-qc.conf`, `~/.isimip-qc.conf`, or `/etc/isimip-qc.conf`. The config file needs to have a section `isimip-qc` and uses lower case variables and underscores, e.g.:
        ```
        [isimip-qc]
        pattern_locations = /path/to/isimip-protocol-3/output/pattern/
        schema_locations = path/to/isimip-protocol-3/output/schema/
        ```

    * environment variables (in caps and with underscores, e.g. `UNCHECKED_PATH`).
* `-c, --copy` and `-m, --move`: Copy or move files that have successfully passed the checks to a final destination.
* `--unchecked-path UNCHECKED_PATH`: Any files in this folder **and** its subfolders will be included into the list of files to test.
* `--checked-path CHECKED_PATH`: Target folder for the `--copy` or `--move` operation. The subfolder structure below CHECKED_PATH will be created and filled according to the sub-structure found in UNCHECKED_PATH
* `--protocol-location PROTOCOL_LOCATIONS`: For working with local copies of the ISIMIP protocol (append `/output` to the cloned repositories). Omit for using the online GitHub protocol versions for [ISIMIP2](https://github.com/ISI-MIP/isimip-protocol-2) or [ISIMIP3](https://github.com/ISI-MIP/isimip-protocol-3)
* `--log-level LOG_LEVEL`: Set the detail level of log output. Default is WARNING while INFO also gives feedback on successful tests. ERROR or CRITICAL will only report very severe issues.
* `--log-path LOG_PATH`: Also write the logs to a file where the folder structure below LOG_PATH is taken from UNCHECKED_PATH.
* `-f, --first-file`: Only test the first file found in UNCHECKED_PATH. Usefull for revealing issues that may occur on all your files.
* `-w, --stop-on-warnings`: The tool will stop after the first file where WARNINGs have been identified.
* `-e, --stop-on-errors`: The tool will stop after the first file where ERRORs have been identified.
* `-r [MINMAX], --minmax [MINMAX]`: Test the data for valid ranges when defined in the protocol. Per default and when violations are detected the top 20 minimum and maximum values along with their time and geographic location will be logged as well. MINMAX is optional and defines how many values should be reported instead. This test drastically slows down the run time of the tool.
* `--fix`: This option activates a number of fixes for WARNINGs by taking the default values from the protocol, e.g. variable attributes and units. In additions an unique identifier (UUID), the version of this tool and the protocol version (by a git hash) are being written to the global attributes section of the NetCDF file. **Attention**: Tixes and are going to be applied on **your original files** in UNCHECKED_PATH.
* `--fix-datamodel`: Fixes to the data model and compression level of the NetCDF file can't be made on-the-fly with the libraries used by the tool. We here rely on one of the external tools [cdo](https://code.mpimet.mpg.de/projects/cdo/) or nccopy (from the [NetCDF library](https://www.unidata.ucar.edu/software/netcdf/)) to rewrite the entire file. Please try to create the files with the proper data model (compressed NETCDF4_CLASSIC) in your postprocessing chain before submitting them to the data server.
* `--check CHECK`: Perform only one particular check. The list of CHECKs can be taken from the funtions defined in the `isimip_qc/checks/*.py` files.

