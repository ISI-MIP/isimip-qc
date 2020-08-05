ISIMIP quality control
======================

[![Python Version](https://img.shields.io/badge/python-3.7|3.8-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](https://github.com/ISI-MIP/isimip-qc/blob/master/LICENSE)
[![Build Status](https://travis-ci.org/ISI-MIP/isimip-qc.svg?branch=master)](https://travis-ci.org/ISI-MIP/isimip-qc)
[![Coverage Status](https://coveralls.io/repos/github/ISI-MIP/isimip-qc/badge.svg?branch=master)](https://coveralls.io/github/ISI-MIP/isimip-qc?branch=master)

A command line tool for the quality control of climate impact data of the ISIMIP project.

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
usage: isimip-qc [-h] [--copy] [--move] [--config-file CONFIG_FILE]
                 [--unchecked-path UNCHECKED_PATH]
                 [--checked-path CHECKED_PATH]
                 [--pattern-location PATTERN_LOCATION]
                 [--schema-location SCHEMA_LOCATION] [--log-level LOG_LEVEL]
                 [--log-path LOG_PATH]
                 simulation_round sector

positional arguments:
  simulation_round      ISIMIP simulation_round, e.g. ISIMIP3a
  sector                ISIMIP sector, e.g. water_global

optional arguments:
  -h, --help            show this help message and exit
  --copy                Copy checked files to the CHECKED_PATH
  --move                Move checked files to the CHECKED_PATH
  --config-file CONFIG_FILE
                        File path to the config file
  --unchecked-path UNCHECKED_PATH
                        base path of the unchecked files
  --checked-path CHECKED_PATH
                        base path for the checked files
  --pattern-location PATTERN_LOCATION
                        URL or file path to the pattern json
  --schema-location SCHEMA_LOCATION
                        URL or file path to the json schema
  --log-level LOG_LEVEL
                        Log level (ERROR, WARN, INFO, or DEBUG)
  --log-path LOG_PATH   base path for the log files for individual files
```

The only mandatory options are the simulation_round and the sector to be considered. Default values for the optional arguments are set in the code, but can also be provided via:

* a config file given by `--config-file`, or located at `isimip-qc.conf`, `~/.isimip-qc.conf`, or `/etc/isimip-qc.conf`. The config file needs to have a section `isimip-qc` and uses lower case variables and underscores, e.g.:
    ```
    [isimip-qc]
    pattern_locations = /path/to/isimip-protocol-3/output/pattern/
    schema_locations = path/to/isimip-protocol-3/output/schema/
    ```

* environment variables (in caps and with underscores, e.g. `UNCHECKED_PATH`).
