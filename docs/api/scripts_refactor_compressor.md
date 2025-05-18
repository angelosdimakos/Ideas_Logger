# `scripts/refactor/compressor`


## `scripts\refactor\compressor\__init__`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |


## `scripts\refactor\compressor\merged_report_squeezer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `_get_or_add`
Return ID for *triple*; create a new one if unseen.

#### `_calc_percent`
Return overall file-coverage percentage if the *complexity* section
provides enough data, otherwise None.

#### `compress_obj`
Return a *compact* structure with docstrings hoisted into a lookup table.
Parameters
----------
original
The full‑fidelity merged_report dict loaded from JSON.
retain_keys
If True, keep verbose dict keys inside each docstring record instead of
positional arrays.  (Adds ~2 kB gzipped – handy for debugging.)

#### `decompress_obj`
Rebuild the full merged_report structure from the compact *blob*.

#### `_expand`
*No description available.*

#### `_load_json`
*No description available.*

#### `_dump_json`
*No description available.*

#### `_cli`
*No description available.*


## `scripts\refactor\compressor\strictness_report_squeezer`

**🧠 Docstring Summary**

| Section | Content |
|---------|---------|
| Description | *No module description available.* |
| Args | — |
| Returns | — |

### 🛠️ Functions
#### `compress_obj`
Compress a strictness report into a minimal 'modules' mapping.

#### `decompress_obj`
Rebuild the full strictness report structure from the compact blob.

#### `semantic_equal`
Compare two reports semantically, allowing for rounding discrepancies.

#### `_load_json`
*No description available.*

#### `_dump_json`
*No description available.*

#### `_cli`
*No description available.*
