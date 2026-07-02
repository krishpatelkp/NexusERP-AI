"""
==========================================================
NexusERP-AI  |  data_exchange  |  importers.py
==========================================================

File-reading layer ONLY.

Responsibilities:
  - Read .xlsx files (ExcelImporter)
  - Read .csv files  (CSVImporter)
  - Return a list of raw dicts (one per row)
  - Normalise column headers

Rules:
  - NO business logic
  - NO database access
  - NO validation
  - Raise MalformedFileError / EmptyFileError only for
    unrecoverable file-level problems
==========================================================
"""

import io
import csv

from .exceptions import EmptyFileError, MalformedFileError, TooManyRowsError
from .constants  import MAX_IMPORT_ROWS
from .utils      import normalise_headers


# ==========================================================
# BASE IMPORTER
# ==========================================================

class BaseImporter:
    """
    Abstract base for all importers.

    Subclasses implement _read() and return
    a list of raw row dicts with normalised keys.
    """

    def read(self, file):
        """
        Entry point.

        Args:
            file: Django uploaded file object.

        Returns:
            list[dict]: Raw rows with normalised header keys.

        Raises:
            EmptyFileError, TooManyRowsError, MalformedFileError
        """
        rows = self._read(file)

        if not rows:
            raise EmptyFileError(
                "The uploaded file contains no data rows. "
                "Please fill in at least one row and re-upload."
            )

        if len(rows) > MAX_IMPORT_ROWS:
            raise TooManyRowsError(
                f"The file contains {len(rows):,} rows which exceeds the "
                f"maximum allowed limit of {MAX_IMPORT_ROWS:,} rows per import. "
                "Please split the file into smaller batches."
            )

        return rows

    def _read(self, file):
        raise NotImplementedError


# ==========================================================
# EXCEL IMPORTER
# ==========================================================

class ExcelImporter(BaseImporter):
    """
    Reads .xlsx files using openpyxl.

    Design:
        - Reads the first worksheet only.
        - Row 1 is treated as the header.
        - Empty rows (all cells blank) are skipped.
        - Cell values are returned as Python native types
          (date, datetime, float, int, str, None).
    """

    def _read(self, file):
        try:
            import openpyxl
        except ImportError:
            raise MalformedFileError(
                "openpyxl is not installed. "
                "Run: pip install openpyxl"
            )

        try:
            workbook = openpyxl.load_workbook(
                file,
                read_only=True,
                data_only=True,
            )
        except Exception as exc:
            raise MalformedFileError(
                f"Could not open the Excel file: {exc}. "
                "Ensure the file is a valid .xlsx file."
            )

        worksheet = workbook.active
        rows_iter = worksheet.iter_rows(values_only=True)

        # Read header row
        try:
            raw_headers = next(rows_iter)
        except StopIteration:
            raise EmptyFileError(
                "The Excel file has no header row."
            )

        headers = normalise_headers([
            str(h) if h is not None else ""
            for h in raw_headers
        ])

        result = []
        for row_values in rows_iter:
            # Skip completely empty rows
            if all(v is None or str(v).strip() == "" for v in row_values):
                continue

            row_dict = {}
            for header, value in zip(headers, row_values):
                if header:  # ignore blank header columns
                    row_dict[header] = value

            result.append(row_dict)

        workbook.close()
        return result


# ==========================================================
# CSV IMPORTER
# ==========================================================

class CSVImporter(BaseImporter):
    """
    Reads .csv files.

    Design:
        - Auto-detects delimiter (comma, semicolon, tab).
        - Row 1 is treated as the header.
        - Empty rows are skipped.
        - All values are returned as strings.
    """

    def _read(self, file):
        try:
            raw_content = file.read()
            # Try common encodings
            for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
                try:
                    text = raw_content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise MalformedFileError(
                    "Could not decode the CSV file. "
                    "Please save the file as UTF-8 and re-upload."
                )
        except Exception as exc:
            raise MalformedFileError(
                f"Could not read the CSV file: {exc}"
            )

        # Auto-detect delimiter
        sample  = text[:4096]
        dialect = self._detect_dialect(sample)

        reader  = csv.DictReader(io.StringIO(text), dialect=dialect)

        try:
            raw_headers = reader.fieldnames or []
        except Exception:
            raise MalformedFileError(
                "The CSV file appears to be malformed. "
                "Check for unclosed quotes or mixed delimiters."
            )

        headers = normalise_headers(raw_headers)

        result = []
        for row in reader:
            # Build normalised dict
            row_dict = {
                normalise_headers([k])[0]: v
                for k, v in row.items()
                if k is not None
            }

            # Skip empty rows
            if all(not v or str(v).strip() == "" for v in row_dict.values()):
                continue

            result.append(row_dict)

        return result

    @staticmethod
    def _detect_dialect(sample):
        """Auto-detect CSV dialect from a sample of the file."""
        try:
            return csv.Sniffer().sniff(sample, delimiters=",;\t|")
        except csv.Error:
            return csv.excel   # default to comma-separated


# ==========================================================
# IMPORTER FACTORY
# ==========================================================

def get_importer(filename):
    """
    Return the correct importer for the given filename.

    Args:
        filename (str): Original filename from upload.

    Returns:
        BaseImporter subclass instance.

    Raises:
        MalformedFileError for unrecognised extensions.
    """
    lower = filename.lower()
    if lower.endswith(".xlsx"):
        return ExcelImporter()
    if lower.endswith(".csv"):
        return CSVImporter()
    raise MalformedFileError(
        f"Unrecognised file extension for '{filename}'. "
        "Supported: .xlsx, .csv"
    )
