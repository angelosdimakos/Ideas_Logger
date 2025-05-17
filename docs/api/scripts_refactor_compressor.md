# Docstring Report for `scripts/refactor/compressor/`


## `scripts\refactor\compressor\__init__`


## `scripts\refactor\compressor\merged_report_squeezer`


### Functions

#### _get_or_add

Return ID for *triple*; create a new one if unseen.

#### _calc_percent

Return overall file-coverage percentage if the *complexity* section
provides enough data, otherwise None.

#### compress_obj

Return a *compact* structure with docstrings hoisted into a lookup table.
Parameters
----------
original
The full‑fidelity merged_report dict loaded from JSON.
retain_keys
If True, keep verbose dict keys inside each docstring record instead of
positional arrays.  (Adds ~2 kB gzipped – handy for debugging.)

#### decompress_obj

Rebuild the full merged_report structure from the compact *blob*.

#### _expand

#### _load_json

#### _dump_json

#### _cli

## `scripts\refactor\compressor\strictness_report_squeezer`


### Functions

#### compress_obj

Compress a strictness report into a minimal 'modules' mapping.

#### decompress_obj

Rebuild the full strictness report structure from the compact blob.

#### semantic_equal

Compare two reports semantically, allowing for rounding discrepancies.

#### _load_json

#### _dump_json

#### _cli