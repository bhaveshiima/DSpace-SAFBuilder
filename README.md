# DSpace-SAFBuilder

**Bulk Import data into DSpace from a CSV file**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey)

The original SAFBuilder tool stopped working with newer versions of DSpace. This project brings it back as a lightweight Python script — no Java, no GUI, just a single command.

This tool takes a UTF-8 CSV spreadsheet and a set of files and converts them into the **DSpace Simple Archive Format (SAF)** — a structured directory ready for batch import into a DSpace repository.

> Adapted and simplified from [dspace-csv-archive](https://github.com/lib-uoguelph-ca/dspace-csv-archive).

> **Compatibility:** Designed for **DSpace 7 and above**. Tested on **DSpace 9.2**.

### Key Features
- Works with **DSpace 7+** — tested on DSpace 9.2
- Converts each CSV row into an individual DSpace item directory
- Supports Unicode characters in metadata
- Automatically strips diacritics from filenames
- Handles multiple metadata schemas (Dublin Core and custom schemas)
- Supports multi-value fields and language-tagged columns
- No third-party dependencies — standard library only

---

## Project Structure

```
DSpace-SAFBuilder/
├── dspace-csv-safbuilder.py   # Entry point — run this script
├── dspacearchive.py           # Item, ItemFactory, and DspaceArchive classes
├── demo/
│   ├── sample.csv             # Sample CSV file for testing
│   ├── test1.pdf              # Sample PDF referenced in sample.csv (item 1)
│   └── test2.pdf              # Sample PDF referenced in sample.csv (item 2)
├── LICENSE
└── readme.md
```

---

## Requirements

- [Python](https://www.python.org/) 3.8 or later
- No third-party packages required

### Check your Python version

```bash
python3 --version
```

If Python is not installed or not found, install it (Linux/Ubuntu):

```bash
# Update the list of available packages
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip

# Verify installation
python3 --version
```

---

## Installation

Clone the repository to your server (e.g. under `/dspace`):

```bash
# Navigate to the dspace directory
cd /dspace

# Clone the repository
git clone https://github.com/bhaveshiima/DSpace-SAFBuilder.git

# Enter the project folder
cd DSpace-SAFBuilder
```

---

## CSV Spreadsheet Rules

| Rule | Detail |
|------|--------|
| First row | Must be the header row defining column names |
| `files` column | **Required.** Paths to files relative to the CSV file's location. Use `\|\|` to separate multiple files per item. |
| Metadata columns | Use fully qualified Dublin Core names — e.g. `dc.title`, `dc.contributor.author` |
| Multiple schemas | Non-DC metadata uses the schema prefix — e.g. `local.identifier` |
| Language tags | All three formats are supported: `dc.title en` (space), `dc.title [en]` (space + brackets), `dc.title[en]` (brackets only) |
| Multiple values | Separate values with double-pipe `\|\|` — e.g. `author1\|\|author2` |
| Commas in values | Wrap the cell in double quotes — e.g. `"Roses are red, violets are blue"` |
| Column order | Does not matter |

---

## Sample Data (Quick Test)

The repository includes a `demo/` folder with ready-to-use sample files so you can test the tool immediately after cloning without needing your own data.

| File | Description |
|------|-------------|
| `demo/sample.csv` | Sample CSV with 2 items referencing `test1.pdf` and `test2.pdf` |
| `demo/test1.pdf` | Sample PDF file used as a bitstream in item 1 |
| `demo/test2.pdf` | Sample PDF file used as a bitstream in item 2 |

### demo/sample.csv structure

The sample uses the space-separated language format (`dc.title en`) — one of the three supported styles.

| files | dc.title en | dc.date.issued | dc.subject en | dc.type | dc.format.mimetype |
|-------|------------|----------------|---------------|---------|-------------------|
| test1.pdf | Title 1 | 2026 | Bulkimport \|\| Test1 | Document | application/pdf |
| test2.pdf | Title 2 | 2025 | Test2 \|\| Test1 | Article | application/pdf |

### Run the sample

```bash
# From inside the cloned DSpace-SAFBuilder folder
python3 dspace-csv-safbuilder.py demo/sample.csv
```

This will generate a `SimpleArchiveFormat/` directory inside `demo/` with two item directories (`item_001` and `item_002`), each containing a `dublin_core.xml`, a `contents` file, and the corresponding PDF.

```
demo/
├── sample.csv
├── test1.pdf
├── test2.pdf
└── SimpleArchiveFormat/
    ├── item_001/
    │   ├── contents
    │   ├── dublin_core.xml
    │   └── test1.pdf
    └── item_002/
        ├── contents
        ├── dublin_core.xml
        └── test2.pdf
```

---

## Step-by-Step Usage

### Step 1 — Create a working folder

Create a folder for your batch import inside the project directory and place your CSV file and all referenced files inside it:

```bash
# Navigate to the project folder
cd /dspace/DSpace-SAFBuilder

# Create your import folder
mkdir bulk_import
```

Your folder should look like this before running the script:

```
bulk_import/
├── data.csv
├── file1.pdf
├── file2.pdf
└── file3.pdf
```

### Step 2 — Verify your files

```bash
cd /dspace/DSpace-SAFBuilder/bulk_import/

# List all files to confirm everything is in place
ls
```

### Step 3 — Run the SAF builder

Pass the path to your CSV file. The script will automatically create a `SimpleArchiveFormat/` directory next to it.

```bash
python3 /dspace/DSpace-SAFBuilder/dspace-csv-safbuilder.py data.csv
```

On success you will see:

```
Building archive from: data.csv
Archive written to: /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat
```

> **Warning:** Re-running the script will overwrite any existing `SimpleArchiveFormat/` directory. Copy the output somewhere safe before re-running.

### Step 4 — Check the output

```bash
# Navigate to the output directory
cd /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat/

# List all generated item folders
ls
```

The generated structure looks like this:

```
SimpleArchiveFormat/
├── item_001/
│   ├── contents          ← list of bitstream filenames
│   ├── dublin_core.xml   ← Dublin Core metadata as XML
│   ├── file1.pdf
│   └── file2.pdf
└── item_002/
    ├── contents
    ├── dublin_core.xml
    └── file3.pdf
```

Each `dublin_core.xml` looks like:

```xml
<dublin_core schema="dc">
<dcvalue element="title" language="en">Title One</dcvalue>
<dcvalue element="contributor" qualifier="author" language="en">Author One</dcvalue>
<dcvalue element="date" qualifier="issued">2026</dcvalue>
<dcvalue element="subject" language="en">Subject 1</dcvalue>
<dcvalue element="type">Report</dcvalue>
<dcvalue element="format" qualifier="mimetype">application/pdf</dcvalue>
</dublin_core>
```

> **Note:** The `schema="dc"` attribute is always present on the root tag. For non-Dublin Core schemas (e.g. `local.*`), a separate file `metadata_local.xml` is created with `<dublin_core schema="local">`.

### Step 5 — Import into DSpace

The DSpace CLI commands below import the generated archive into your repository. All commands must be run as the `dspace` user on the server.

#### Prerequisites — Set correct ownership

Before importing, make sure the `dspace` user can read and write the archive directory:

```bash
sudo chown -R dspace:dspace /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat
```

#### Command flags reference

| Flag | Description | Example |
|------|-------------|---------|
| `--eperson` / `-e` | Email address of the importing DSpace user | `admin@yourinstitution.edu` |
| `--collection` / `-c` | Handle of the target DSpace collection | `123456789/13` |
| `--source` / `-s` | Path to the `SimpleArchiveFormat` folder | see commands below |
| `--mapfile` / `-m` | Path where the mapfile will be written (keep this!) | see commands below |
| `--add` / `-a` | Specifies an add/import operation | — |
| `--validate` | Dry-run validation — no data is written | — |
| `-d` | Delete/undo a previous import using a mapfile | — |

#### Validate (dry run — no data written)

Always validate first. This checks your archive for errors without importing anything:

```bash
/dspace/bin/dspace import --add --validate \
  --eperson=admin@yourinstitution.edu \
  --collection=123456789/13 \
  --source=/dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat \
  --mapfile=/dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat/data.map
```

If validation passes with no errors, proceed to the actual import.

#### Import

```bash
/dspace/bin/dspace import -a \
  -e admin@yourinstitution.edu \
  -c 123456789/13 \
  -s /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat/ \
  -m /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat/data.map
```

> **Important:** Keep the `data.map` mapfile. It records every imported item and is required to undo or modify the import later.

#### Delete / Undo an import

If the import did not go as planned, use the mapfile to reverse it:

```bash
/dspace/bin/dspace import \
  -e admin@yourinstitution.edu \
  -d \
  -m /dspace/DSpace-SAFBuilder/bulk_import/SimpleArchiveFormat/data.map
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| `Error: file not found` | Path passed to the script does not exist | Check the CSV path is correct and the file exists |
| `KeyError` on a column | `files` column is missing from the CSV header | Add a `files` column to your CSV |
| Files not copied | File paths in CSV are not relative to the CSV file's location | Use relative paths, not absolute paths |
| Garbled or missing filenames | Filename contains diacritics or non-ASCII characters | The tool strips them automatically — no action needed |
| XML validation error in DSpace | Raw `<`, `>`, or `&` characters in metadata values | The tool escapes these automatically — ensure your CSV is saved as UTF-8 |
| Import fails after validate passes | `SimpleArchiveFormat` folder not accessible by `dspace` user | Run `sudo chown -R dspace:dspace <folder>` |
| Wrong XML tag in metadata file | Schema prefix in CSV header does not match `dc` | Check column names start with `dc.` for Dublin Core |
| DSpace error: `Metadata field does not exist` | Language code ended up inside the field name (old SAFBuilder bug) | Use any supported format: `dc.title en`, `dc.title [en]`, or `dc.title[en]` — all are handled correctly |

---

## Contributing

Contributions, bug reports, and feature requests are welcome.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Further Reading

- [DSpace Simple Archive Format documentation](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379125946/Importing+and+Exporting+Items+via+Simple+Archive+Format)
- [Original dspace-csv-archive project](https://github.com/lib-uoguelph-ca/dspace-csv-archive)
