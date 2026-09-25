# Changelog

## [isimip-qc 4.1](https://github.com/ISI-MIP/isimip-qc/releases/tag/4.1)

### Main improvements

* CLI & UX improvements
  * Add `--check-isimip-id` option: test for duplicate `isimip_id` on the ISIMIP repository only when explicitly requested (it was previously queried for every file)
  * Check for a newer `isimip-qc` version on PyPI at startup, and abort with a clear error message when no internet connection is available
  * Reject unknown `--check` names instead of silently skipping all checks
  * Align `--ignore-critical` and `--force-copy-move` with their actual behaviour: copying or moving files with critical issues now requires both options, and files with critical issues now get a proper verdict logged
  * Validate the `schema_path` argument and fail with a clear error message
  * Drop the special `any` string in `--include` lists (unmatched include lists already pass all files)
* Data handling & checks
  * Take grid definitions from the protocol instead of hardcoded values, with sector-specific, model-specific and climate-forcing grids
  * Add `valid_min`/`valid_max` checks for sector-specific grids
  * Add a check for string length dimensions (e.g. `string32` = 32)
  * Check the data types of dimension variables against the protocol (replaces the hardcoded `vertical` dtype check)
  * Improve the `contact` attribute check: new regex-based parser, allow multiple contacts separated by semicolons (normalized to commas)
  * Check the `classes` attribute of the `fuelclass` variable (forestry)
  * Support forestry plot-based data, announcing exemptions from grid checks at `INFO`
  * Minor adjustments for 3d variables in the biodiversity sector
  * Accept the corrected calendar key of the protocol and drop the fallback to the legacy spelling, as well as the stale `calendars_daily` fallback
* Robustness & bug fixes
  * No more crashes on broken or degenerate files: dimension, lat/lon and time checks against empty axes or missing protocol entries now report issues instead of aborting the run
  * Missing protocol entries no longer crash the run summary, and a failing `--fix-datamodel` no longer aborts the whole batch
  * Skip copying or moving a file onto itself (which happened when checked files already live inside `CHECKED_PATH`)
  * Keep a pattern without a suffix constraint from crashing the file walk
  * Skip the protocol version check when definitions carry no commit hash
  * Report the dimension order only once, compare units as strings before comparison, and give the file check state safe defaults so individual checks can run standalone
* Documentation
  * Add the DOI to README and `CITATION.cff`
  * Update README to match the behaviour of `--ignore-critical`, `--force-copy-move` and the copy/move handling

**Commit history**: [4.0...4.1](https://github.com/ISI-MIP/isimip-qc/compare/4.0...4.1)

## [isimip-qc 4.0](https://github.com/ISI-MIP/isimip-qc/releases/tag/4.0)

### Main improvements

* Refactoring & performance
  * Refactor and optimize
  * Integrate the new `isimip_utils` version
  * Improve performance when iteration over large file trees
* CLI & UX improvements
  * Use [TOML](https://toml.io/en/) syntax for config files and `.toml` suffix for default config locations
  * Environment variables use `ISIMIP_` as prefix
  * Add `--show-time` and `--show-path` options
  * Add `--summary`, `--match-only` and `--minmax-values` options
  * Improve logging and remove obsolete log levels
  * Use summary tables for console output
* Data handling & checks
  * Allow for integer dtypes for the `bin` variable
  * Add fallbacks in dimension handling
  * Relax and improve parsing of the contact attribute (disable strict checking; print parsed name and email)

**Commit history**: [3.5...4.0](https://github.com/rdmorganiser/rdmo/compare/3.5...4.0)
