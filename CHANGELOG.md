# Changelog

Starting from commit 60720a85b5e9a8cc878b378df68751989452170d

This file summarizes notable changes made since the given base commit.

## Summary of changes

- **Refactoring & performance:** Large refactors and optimizations were applied to the codebase, including merges from the `isimip_utils` workstream and general cleanup of internals.

- **Bug fixes:** Several correctness fixes were implemented, for example:
	- fixes for string casing handling
	- corrected checks for the direction of the depth dimension
	- other small check fixes improving validation behavior

- **CLI & UX improvements:** The command-line interface and logging were improved:
	- added `--show-time` and `--show-path` options
	- added `--summary`, `--match-only` and `--minmax-values` options
	- restored comma-separated lists for `--include`/`--exclude`
	- normalize `--log-level` input (upper-casing)
	- deduplicated INFO log text and removed obsolete log levels
	- use richer summary tables for console output

- **Data handling & checks:** Enhancements to dataset checks and data handling:
	- allowed integer dtypes for the `bin` variable
	- added fallbacks in dimension handling
	- improved DidNotMatch error handling and path include/exclude methods

- **Contact/metadata handling:** Relaxed and improved parsing of the contact attribute (disable strict checking; print parsed name and email).

- **Dependencies & compatibility:** Updated dependencies and project metadata to target a new minimum Python version and to use newer `isimip-utils` APIs (e.g., protocol parsing and location utilities).
