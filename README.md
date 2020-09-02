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


Setup
-----

The tool can be installed via pip. Usually you want to create a [virtual environment]() first.

```bash
# setup venv
python3 -m venv env
source env/bin/activate

# install from GitHub
pip install git+https://github.com/ISI-MIP/isimip-qc
```

Usage
-----

The tool has several options which can be inspected using the help option `-h, --help`:

```plain
usage: isimip-qc [-h] [--config-file CONFIG_FILE] [-c] [-m]
                 [--unchecked-path UNCHECKED_PATH] [--checked-path CHECKED_PATH]
                 [--protocol-location PROTOCOL_LOCATIONS]
                 [--log-level LOG_LEVEL] [--log-path LOG_PATH]
                 [-f] [-w] [-e] [-r]
                 [--fix] [--check CHECK]
                 schema_path

Check ISIMIP files for matching protocol definitions

positional arguments:
  schema_path           ISIMIP schema_path, e.g.
                        ISIMIP3a/OutputData/water_global

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        File path of the config file
  -c, --copy            Copy checked files to CHECKED_PATH
  -m, --move            Move checked files to CHECKED_PATH
  --unchecked-path UNCHECKED_PATH
                        base path of the unchecked files
  --checked-path CHECKED_PATH
                        base path for the checked files
  --protocol-location PROTOCOL_LOCATIONS
                        URL or file path to the protocol
                        when different from official repository
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-path LOG_PATH   base path for the individual log files
  -f, --first-file      only process first file found in UNCHECKED_PATH
  -w, --stop-on-warnings
                        stop execution on warnings
  -e, --stop-on-errors  stop execution on errors
  -r, --minmax          test values for valid range (slow)
  --fix                 try to fix warnings detected on the original files
  --check CHECK         perform only one particular check```

The only mandatory option is the `schema_path`, which specifies the pattern and schema to use. The `schema_path` consitst of the `simulation_round`, the `product`, and the `sector` seperated by slashes, e.g. `ISIMIP3a/OutputData/water_global`.

Caution: With the `--fix` option the fixes are going to be applied on your original files in UNCHECKED_PATH.

Default values for the optional arguments are set in the code, but can also be provided via:

* a config file given by `--config-file`, or located at `isimip-qc.conf`, `~/.isimip-qc.conf`, or `/etc/isimip-qc.conf`. The config file needs to have a section `isimip-qc` and uses lower case variables and underscores, e.g.:
    ```
    [isimip-qc]
    pattern_locations = /path/to/isimip-protocol-3/output/pattern/
    schema_locations = path/to/isimip-protocol-3/output/schema/
    ```

* environment variables (in caps and with underscores, e.g. `UNCHECKED_PATH`).
