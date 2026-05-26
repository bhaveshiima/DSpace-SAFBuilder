"""
DSpace Simple Archive Format (SAF) builder.

Reads a UTF-8 CSV file and produces a SAF directory tree ready for
batch import into a DSpace repository.

See: https://wiki.lyrasis.org/pages/viewpage.action?pageId=104566653
"""

import os
import re
import csv
import unicodedata
from shutil import copy


# XML output always uses \n regardless of OS line separator.
_LINESEP = b'\n'


class Item:
    """Represents a single DSpace item: metadata attributes and associated files."""

    DELIMITER = b'||'

    def __init__(self, delimiter=b'||'):
        self.delimiter = delimiter
        self._attributes = {}
        self.files = b''

    def getAttributes(self):
        """Return the dict of all metadata attributes."""
        return self._attributes

    def setAttribute(self, attribute, value):
        """Set a metadata attribute or the files field from a string value."""
        encoded = (value or '').encode('utf-8')
        if attribute == b'files':
            self.files = encoded
        else:
            self._attributes[attribute] = encoded

    def getAttribute(self, attribute):
        """Return the bytes value for a single metadata attribute."""
        return self._attributes[attribute]

    def __str__(self):
        return str(self._attributes)

    def getFiles(self):
        """Return bare filenames (no path) for this item's bitstreams."""
        return [os.path.basename(f).strip() for f in self.files.split(self.delimiter) if f.strip()]

    def getFilePaths(self):
        """Return relative file paths for this item's bitstreams."""
        return [f.strip() for f in self.files.split(self.delimiter) if f.strip()]

    def toXML(self, schema=b'dc'):
        """Return a bytes XML representation of this item for the given schema."""
        if schema != b'dc':
            header = b'<dublin_core schema="' + schema + b'">' + _LINESEP
        else:
            header = b'<dublin_core>' + _LINESEP

        lines = [header]
        for key, value in self._attributes.items():
            if not key.startswith(schema):
                continue
            tag_open = self._build_open_tag(key)
            for val in value.split(self.delimiter):
                val = val.strip()
                if val:
                    lines.append(tag_open + self._escape(val) + b'</dcvalue>' + _LINESEP)
        lines.append(b'</dublin_core>' + _LINESEP)
        return b''.join(lines)

    def _build_open_tag(self, attribute):
        """Build the opening <dcvalue ...> tag for a metadata attribute key."""
        lang = self._lang_attr(attribute)
        base = attribute.split(b'#lang#')[0]
        parts = base.split(b'.')
        element = b' element="' + self._escape(parts[1]) + b'" ' if len(parts) >= 2 else b''
        qualifier = b' qualifier="' + self._escape(parts[2]) + b'" ' if len(parts) >= 3 else b''
        return b'<dcvalue' + element + qualifier + lang + b'>'

    def _lang_attr(self, attribute):
        """Extract the language XML attribute string from a metadata key, or empty bytes."""
        match = re.search(rb'#lang#(\w+)', attribute)
        return b' language="' + self._escape(match.group(1)) + b'" ' if match else b''

    def _escape(self, s, quote=False):
        """Escape XML special characters in a bytes string."""
        s = s.replace(b'&', b'&amp;')  # must be first
        s = s.replace(b'<', b'&lt;')
        s = s.replace(b'>', b'&gt;')
        if quote:
            s = s.replace(b'"', b'&quot;')
            s = s.replace(b"'", b'&#x27;')
        return s


class ItemFactory:
    """Creates Item objects from a CSV header and data rows."""

    def __init__(self, header):
        self.header = [self._normalize_column(col) for col in header]

    def _normalize_column(self, column):
        """Convert a CSV column name to the internal bytes key format.

        Handles all three language tag styles found in CSV headers:
          dc.title [en]   -> dc.title#lang#en  (brackets with space)
          dc.title[en]    -> dc.title#lang#en  (brackets without space)
          dc.title en     -> dc.title#lang#en  (space only, no brackets)
        """
        col = column.encode('utf-8').strip()
        col = col.replace(b' [', b'#lang#')   # "dc.title [en]"
        col = col.replace(b' ', b'#lang#')    # "dc.title en"
        col = col.replace(b'[', b'#lang#')    # "dc.title[en]"
        col = col.replace(b']', b'')
        return col

    def newItem(self, values=None):
        """Create and return a new Item from a CSV data row."""
        item = Item()
        row = values or [''] * len(self.header)
        for column, value in zip(self.header, row):
            item.setAttribute(column, value or '')
        return item


class DspaceArchive:
    """Reads a CSV file and produces a DSpace SAF directory tree."""

    def __init__(self, input_path):
        self.input_base_path = os.path.dirname(os.path.abspath(input_path))
        self.items = []
        with open(input_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)
            factory = ItemFactory(header)
            for row in reader:
                self.items.append(factory.newItem(row))

    def addItem(self, item):
        """Append an item to the archive."""
        self.items.append(item)

    def getItem(self, index):
        """Return the item at the given index."""
        return self.items[index]

    def write(self, output_dir='.'):
        """Write the archive to disk in DSpace SAF format."""
        os.makedirs(output_dir, exist_ok=True)
        for index, item in enumerate(self.items):
            item_path = os.path.join(output_dir, f"item_{index + 1:03d}")
            os.makedirs(item_path, exist_ok=True)
            self._write_contents(item, item_path)
            self._copy_files(item, item_path)
            self._write_metadata(item, item_path)

    def _write_contents(self, item, item_path):
        """Write the contents file listing all bitstream filenames, one per line."""
        files = item.getFiles()
        contents = b'\n'.join(self._normalize_unicode(f) for f in files) + b'\n'
        with open(os.path.join(item_path, 'contents'), 'wb') as f:
            f.write(contents)

    def _copy_files(self, item, item_path):
        """Copy bitstream files from the source directory into the item directory."""
        for file_path in item.getFilePaths():
            file_str = file_path.decode('utf-8')
            src = os.path.join(self.input_base_path, file_str)
            dst = os.path.join(item_path, self._normalize_unicode(file_path).decode('utf-8'))
            copy(src, dst)

    def _get_metadata_schemas(self):
        """Return the unique schema prefixes used in the first item's attributes."""
        schemas = []
        for key in self.items[0].getAttributes():
            prefix = key.split(b'.')[0]
            if prefix and prefix not in schemas:
                schemas.append(prefix)
        return schemas

    def _write_metadata(self, item, item_path):
        """Write one XML metadata file per schema into the item directory."""
        for schema in self._get_metadata_schemas():
            filename = 'dublin_core.xml' if schema == b'dc' else f"metadata_{schema.decode('utf-8')}.xml"
            with open(os.path.join(item_path, filename), 'wb') as f:
                f.write(item.toXML(schema))

    @staticmethod
    def _normalize_unicode(value):
        """Strip diacritics from a bytes filename and return UTF-8 bytes."""
        return unicodedata.normalize('NFD', value.decode('utf-8')).encode('ascii', 'ignore')
