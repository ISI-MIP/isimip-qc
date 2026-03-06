# Changelog

## [isimip-qc 4.0](https://github.com/ISI-MIP/isimip-qc/releases/tag/4.0)

### Main improvements

* Refactoring & performance
  * Refactor and optimize
  * Integrate the new `isimip_utils` version
  * Improve performance when iteration over large file trees
* CLI & UX improvements
  * Add `--show-time` and `--show-path` options
  * Add `--summary`, `--match-only` and `--minmax-values` options
  * Improve logging and remove obsolete log levels
  * Use summary tables for console output
* Data handling & checks
  * Allow for integer dtypes for the `bin` variable
  * Add fallbacks in dimension handling
  * Relax and improve parsing of the contact attribute (disable strict checking; print parsed name and email)

**Commit history**: [3.5...4.0](https://github.com/rdmorganiser/rdmo/compare/3.5...4.0)
