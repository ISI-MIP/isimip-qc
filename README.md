ISIMIP quality control
======================

[![Python Version](https://img.shields.io/badge/python->=3.6-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/ISI-MIP/isimip-qc/blob/master/LICENSE)

A command line tool for the quality control of climate impact data of the ISIMIP project. It mainly covers tests of:
- the file name against the protocol schemas and patterns
- variables, dimensions and global attributes
- data model and types
- some consistency checks on the NetCDF time axis and
- if the data is within a valid value range (when defined in the ISIMIP protocol)

**This is still work in progress.**


Setup
-----

The application is written in Python (> 3.6) uses only dependencies, which can be installed without administrator priviledges. The installation of Python (and its developing packages), however differs from operating system to operating system. Optional Git is needed if the application is installed directly from GitHub. The installation of Python 3 and Git for different plattforms is documented [here](https://github.com/ISI-MIP/isimip-utils/blob/master/docs/prerequisites.md).

The tool itself can be installed via pip. Usually you want to create a [virtual environment](https://docs.python.org/3/library/venv.html) first, but this is optional.

```bash
# setup venv on Linux/macOS/Windows WSL
python3 -m venv env
source env/bin/activate

# setup venv on Windows cmd
python -m venv env
call env\Scripts\activate.bat

# install from the Python Package Index (PyPI), recommended
pip install isimip-qc

# update from PyPI
pip install --upgrade rdmo

# install directly from GitHub
pip install git+https://github.com/ISI-MIP/isimip-qc

# update from Github
pip install --upgrade git+https://github.com/ISI-MIP/isimip-qc
```

Usage
-----

The tool has several options which can be inspected using the help option `-h, --help`:

```plain
usage: isimip-qc [-h] [--config-file CONFIG_FILE] [-c] [-m] [-O]
                 [--unchecked-path UNCHECKED_PATH] [--checked-path CHECKED_PATH]
                 [--protocol-location PROTOCOL_LOCATIONS] [--log-level LOG_LEVEL]
                 [--log-path LOG_PATH] [--log-path-level LOG_PATH_LEVEL] [--include INCLUDE_LIST]
                 [--exclude EXCLUDE_LIST] [-f] [-w] [-e] [-r [MINMAX]] [-nt] [--fix]
                 [--fix-datamodel [FIX_DATAMODEL]] [--check CHECK] [-V]
                 schema_path

Check ISIMIP files for matching protocol definitions

positional arguments:
  schema_path           ISIMIP schema_path, e.g. ISIMIP3a/OutputData/water_global

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        file path of the config file
  -c, --copy            copy checked files to CHECKED_PATH if no warnings or errors were found
  -m, --move            move checked files to CHECKED_PATH if no warnings or errors were found
  -O, --overwrite       overwrite files in CHECKED_PATH if present. Default is False.
  --unchecked-path UNCHECKED_PATH
                        base path of the unchecked files
  --checked-path CHECKED_PATH
                        base path for the checked files
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol when different from official repository
  --log-level LOG_LEVEL
                        log level (CRITICAL, ERROR, WARN, VRDETAIL, CHECKING, SUMMARY, INFO, or
                        DEBUG) [default: CHECKING]
  --log-path LOG_PATH   base path for the individual log files
  --log-path-level LOG_PATH_LEVEL
                        log level for the individual log files [default: WARN]
  --include INCLUDE_LIST
                        patterns of files to include. Exclude those that don't match any.
  --exclude EXCLUDE_LIST
                        patterns of files to exclude. Include only those that don't match any.
  -f, --first-file      only process first file found in UNCHECKED_PATH
  -w, --stop-on-warnings
                        stop execution on warnings
  -e, --stop-on-errors  stop execution on errors
  -r [MINMAX], --minmax [MINMAX]
                        test values for valid range (slow, argument MINMAX defaults to show the
                        top 10 values)
  -nt, --skip-time-span-check
                        skip check for simulated time period
  --fix                 try to fix warnings detected on the original files
  --fix-datamodel [FIX_DATAMODEL]
                        also fix warnings on data model found using NCCOPY or CDO (slow). Choose
                        preferred tool per lower case argument.
  --check CHECK         perform only one particular check
  -V, --version         show program's version number and exit
```

The only mandatory argument is the `schema_path`, which specifies the pattern and schema to use. The `schema_path` consitst of the `simulation_round`, the `product`, and the `sector` seperated by slashes, e.g. `ISIMIP3a/OutputData/water_global`. If the only argument used is `schema_path`, the current user path when calling the tool should be same as the directory of the files to be checked.

### The options in detail

* `--config-file`: Default values for the optional arguments are set in the code, but can also be provided via:
    * a config file given by `--config-file`, or located at `isimip-qc.conf`, `~/.isimip-qc.conf`, or `/etc/isimip-qc.conf`. The config file needs to have a section `isimip-qc` and uses lower case variables and underscores, e.g.:
        ```
        [isimip-qc]
        pattern_locations = /path/to/isimip-protocol-3/output/pattern/
        schema_locations = path/to/isimip-protocol-3/output/schema/
        ```

    * environment variables (in caps and with underscores, e.g. `UNCHECKED_PATH`).
* `-c, --copy` and `-m, --move`: Copy or move files that have successfully passed the checks to a final destination. Effective only when no warnings have been found on the file.
* '-O, --overwrite`: Allow overwriting of existing files in CHECKED_PATH. Default is to skip copy or move in case the target file is already present.
* `--unchecked-path UNCHECKED_PATH`: Any files in this folder **and** its subfolders will be included into the list of files to test.
* `--checked-path CHECKED_PATH`: Target folder for the `--copy` or `--move` operation. The subfolder structure below CHECKED_PATH will be created and filled according to the sub-structure found in UNCHECKED_PATH
* `--protocol-location PROTOCOL_LOCATIONS`: For working with local copies of the ISIMIP protocol (append `/output` to the cloned repositories folder). Omit option for using the online GitHub protocol versions for [ISIMIP2](https://github.com/ISI-MIP/isimip-protocol-2) or [ISIMIP3](https://github.com/ISI-MIP/isimip-protocol-3). An internet connection is required for reading the online protocols.
* `--log-level LOG_LEVEL`: Set the detail level of log output. Default is `CHECKING`. Log levels from `CRITICAL` to `VRDETAIL` will not show the file currently checked in the terminal but write all of them to the data file specific log file.<br>
`CRITICAL` : only very severe errors<br>
`ERROR`: all errors<br>
`WARN`: warnings and all errors<br>
`VRDETAIL`: same as CHECKING but with details on time and location of valid ranges violations when invoked with `--minmax` option. Very slow when violations are detected.<br>
`CHECKING`: includes warnings and errors<br>
`SUMMARY`: includes warnings, errors and the summary shown at the end<br>
`INFO`: includes `SUMMARY` and details for successful checks<br>
`DEBUG`: all the above plus details for some debugging cases.
* `--log-path LOG_PATH`: Also write the logs to a file where the folder structure below LOG_PATH is taken from UNCHECKED_PATH.
* `--log-path-level LOG_PATH_LEVEL`: The log level used for the file specific logs below `LOG_PATH`. The default is `WARN` and should suffice for most cases.
* `--include INCLUDE_LIST` : Provide a comma-separated list of strings to include for the checks if any of them matches the file path or name, e.g. 'daily,dis' will only check `*daily*` or `*discharge*` files while skipping others.
* `--exclude EXCLUDE_LIST` : Provide a comma-separated list of strings to exclude from the checks if any of them matches the file path or name, e.g. 'monthly,histsoc' will skip any `*monthly*` or `*histsoc*` files.
* `-f, --first-file`: Only test the first file found in UNCHECKED_PATH. Useful for revealing issues that may occur on all your files.
* `-w, --stop-on-warnings`: The tool will stop after the first file where WARNINGs have been identified.
* `-e, --stop-on-errors`: The tool will stop after the first file where ERRORs have been identified.
* `-r [MINMAX], --minmax [MINMAX]`: Test the data for valid ranges when defined in the protocol. Per default and when violations are detected the top 20 minimum and maximum values along with their time and geographic location will be logged as well. MINMAX is optional and defines how many values should be reported instead of 20. This test drastically slows down the run time of the tool.
* -nt, --skip-time-span-check: Skip checking non-dialy data for proper coverage of simulation periods.
* `--fix`: Activates a number of fixes for WARNINGs by taking the default values from the protocol, e.g. variable attributes and units. In additions an unique identifier (UUID), the version of this tool and the protocol version (by a git hash) are being written to the global attributes section of the NetCDF file. **Attention**: Fixes and are going to be applied on **your original files** in UNCHECKED_PATH.
* `--fix-datamodel [FIX_DATAMODEL]`: Fixes to the data model and compression level of the NetCDF file can't be made on-the-fly with the libraries used by the tool. We here rely on the external tools [cdo](https://code.mpimet.mpg.de/projects/cdo/) or nccopy (from the [NetCDF library](https://www.unidata.ucar.edu/software/netcdf/)) to rewrite the entire file. Default is `nccopy`. Please try to create the files with the proper data model (compressed NETCDF4_CLASSIC) in your postprocessing chain before submitting them to the data server.
* `--check CHECK`: Perform only one particular check. The list of CHECKs can be taken from the funtions defined in the `isimip_qc/checks/*.py` files.

