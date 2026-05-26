# DSpace-SAFBuilder
**DSpace SAFBuilder — Bulk Import data from CSV**

This tool takes a simple CSV spreadsheet (UTF-8) and a set of files and converts them into the **DSpace Simple Archive Format (SAF)** — a structured directory ready for batch import into a DSpace repository.

> Adapted and simplified from [dspace-csv-archive](https://github.com/lib-uoguelph-ca/dspace-csv-archive).

### Key Features
- Converts CSV rows into individual DSpace item directories
- Supports Unicode characters in metadata
- Automatically strips diacritics from filenames
- Handles multiple metadata schemas (Dublin Core and custom)
- Supports multi-value fields and language-tagged columns

---

## Project Structure

```
DSpace_SAFBuilder/
├── dspace-csv-archive.py   # Entry point — run this script
├── dspacearchive.py        # Item, ItemFactory, and DspaceArchive classes
└── readme.md
```

---

## Requirements

- [Python](https://www.python.org/) 3.8 or later
- No third-party packages required (standard library only)

### Check your Python version

```bash
python3 --version
```

If Python is not installed or not found, install it:

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
| `files` column | **Required.** Paths to files relative to the CSV file's location. Use `\|\|` to list multiple files per item. |
| Metadata columns | Use fully qualified Dublin Core names — e.g. `dc.title`, `dc.contributor.author` |
| Multiple schemas | Non-DC metadata uses the schema prefix format — e.g. `local.identifier` |
| Language tags | Append the language in brackets after the column name — e.g. `dc.title [en]` or `dc.title[en]` |
| Multiple values | Separate values with double-pipe `\|\|` — e.g. `author1\|\|author2` |
| Commas in values | Wrap the cell in double quotes — e.g. `"Roses are red, violets are blue"` |
| Column order | Does not matter |

### Example CSV

| files | dc.title [en] | dc.contributor.author [en] | dc.subject | dc.type |
|-------|--------------|---------------------------|------------|---------|
| file1.pdf\|\|file2.pdf | Title One | Author One | Subject 1\|\|Subject 3 | Report |
| file3.pdf | "Title Two, with comma" | Author A\|\|Author B | Subject 2 | Article |

---

## Step-by-Step Usage

### Step 1 — Create a working folder

Create a folder for your batch (e.g. `bhavesh_bulkimport`) inside the project directory and put your CSV and all referenced files in it:

```bash
# Navigate to the project folder
cd /dspace/DSpace-SAFBuilder

# Create your import folder
mkdir bhavesh_bulkimport
```

Your folder should look like this before running the script:

```
bhavesh_bulkimport/
├── data.csv
├── file1.pdf
├── file2.pdf
└── file3.pdf
```

### Step 2 — Copy your files and verify

```bash
cd /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/

# List all files to confirm everything is in place
ls
```

### Step 3 — Run the SAF builder

Make sure you are pointing to the CSV file. The script will auto-create a `SimpleArchiveFormat/` directory next to the CSV.

```bash
python3 /dspace/DSpace-SAFBuilder/dspace-csv-archive.py data.csv
```

On success you will see:
```
Building archive from: data.csv
Archive written to: /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat
```

> **Warning:** Re-running the script will overwrite any existing `SimpleArchiveFormat/` directory. Copy the output somewhere safe before re-running.

### Step 4 — Check the output

```bash
ls /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat/
```

The generated structure looks like this:

```
SimpleArchiveFormat/
├── item_001/
│   ├── contents          ← list of bitstream filenames
│   ├── dublin_core.xml   ← DC metadata as XML
│   ├── file1.pdf
│   └── file2.pdf
└── item_002/
    ├── contents
    ├── dublin_core.xml
    └── file3.pdf
```

Each `dublin_core.xml` looks like:

```xml
<dublin_core>
  <dcvalue element="title" language="en">Title One</dcvalue>
  <dcvalue element="contributor" qualifier="author" language="en">Author One</dcvalue>
  <dcvalue element="subject">Subject 1</dcvalue>
  <dcvalue element="type">Report</dcvalue>
</dublin_core>
```

---

## Step 5 — Import into DSpace

The following DSpace CLI commands import the generated archive. All commands must be run as the `dspace` user on the server.

You will need the following details:

| Flag | Description | Example |
|------|-------------|---------|
| `--eperson` / `-e` | Email address of the importing user | `bhaveshiima@gmail.com` |
| `--collection` / `-c` | Handle of the target collection | `123456789/13` |
| `--source` / `-s` | Path to the `SimpleArchiveFormat` folder | see below |
| `--mapfile` / `-m` | Path where the mapfile will be saved (keep this!) | see below |
| `--add` / `-a` | Specifies an add/import operation | — |

### Validate (dry run — no data written)

Always validate first. This checks your archive for errors without importing anything:

```bash
/dspace/bin/dspace import --add --validate \
  --eperson=bhaveshiima@gmail.com \
  --collection=123456789/13 \
  --source=/dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat \
  --mapfile=/dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat/data.map
```

If the validation passes with no errors, proceed to the actual import.

### Import

```bash
/dspace/bin/dspace import -a \
  -e bhaveshiima@gmail.com \
  -c 123456789/13 \
  -s /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat/ \
  -m /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat/data.map
```

> **Important:** Keep the `data.map` mapfile. It records every item that was imported and is required to undo or modify the import later.

### Delete / Undo an import

If the import did not go as planned, use the mapfile to reverse it:

```bash
/dspace/bin/dspace import -e bhaveshiima@gmail.com \
  -d \
  -m /dspace/DSpace-SAFBuilder/bhavesh_bulkimport/SimpleArchiveFormat/data.map
```

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|-------------|-----|
| `Error: file not found` | Path passed to the script does not exist | Check the CSV path is correct and the file exists |
| `KeyError` on a column | `files` column is missing from the CSV header | Add a `files` column to your CSV |
| Files not copied | File paths in CSV are not relative to CSV location | Use paths relative to the CSV file, not absolute paths |
| Garbled filenames | Filename has diacritics or non-ASCII characters | The tool strips them automatically — no action needed |
| XML validation error in DSpace | Raw `<`, `>`, or `&` in metadata values | The tool escapes these automatically — check your CSV encoding is UTF-8 |
| Import fails after validate passes | `SimpleArchiveFormat` folder not accessible by `dspace` user | Run `sudo chown -R dspace:dspace <folder>` |

---

## Further Reading

- [DSpace Simple Archive Format documentation](https://wiki.lyrasis.org/spaces/DSDOC9x/pages/379125946/Importing+and+Exporting+Items+via+Simple+Archive+Format)
- [Original dspace-csv-archive project](https://github.com/lib-uoguelph-ca/dspace-csv-archive)
