# --- Imports --- #
from abc import abstractmethod
from .repository import Repository
import os, csv, json


# --- Classes --- #
class CsvRepository(Repository):
    """Abstract base class for CSV repositories. Provides common functionality for saving and loading data from CSV files.
    Subclasses should implement the _process_data_row method to handle specific data formats.
    """

    def __init__(self, filepath, fieldnames, mode, logger=None):
        self.__filepath = filepath  # Path to the CSV file
        self.__fieldnames = fieldnames  # List of field names for the CSV file
        self.__mode = mode  # Mode for opening the file ('w' for write, 'a' for append)
        self.__logger = logger  # Optional logger for logging messages

        self.__reader = csv.DictReader
        self.__writer = csv.DictWriter

    def _create_empty_file(self) -> None:
        """Creates an empty CSV file with the specified fieldnames."""
        try:
            with open(self.__filepath, mode="w", newline="", encoding="utf-8") as file:
                writer = self.__writer(file, self.__fieldnames)
                writer.writeheader()

        except OSError as error:
            self._log(
                f"[Data Manager] Error: could not create data file '{self.__filepath}' ({error})."
            )

    def save(self, data) -> bool:
        """Saves one record to the CSV file. Returns True if the save succeeded."""
        # Handles creation of new file if it does not exist
        if not os.path.exists(self.__filepath):
            self._create_empty_file()

        try:
            with open(
                self.__filepath, mode=self.__mode, newline="", encoding="utf-8"
            ) as file:
                writer = self.__writer(file, fieldnames=self.__fieldnames)

                if self.__mode == "w":
                    writer.writeheader()
                    writer.writerows(data)

                else:
                    writer.writerow(data)

        except OSError as error:
            self._log(
                f"[Data Manager] Error: could not save to '{self.__filepath}' ({error})."
            )

            return False

        return True

    def load(self) -> list:
        """
        Loads all saved records from the CSV spreadsheet specified.
        """

        # Handles missing CSV file and creates it, does not crash
        if not os.path.exists(self.__filepath):
            self._log(
                f"[Data Manager] No existing data file found at '{self.__filepath}'. Creating a new one."
            )

            self._create_empty_file()
            return []

        records = []

        try:
            with open(self.__filepath, mode="r", newline="", encoding="utf-8") as file:
                reader = self.__reader(file)

                if reader.fieldnames is None or set(reader.fieldnames) != set(
                    self.__fieldnames
                ):
                    # Logs if there is an error reading file
                    self._log(
                        f"[Data Manager] Warning: '{self.__filepath}' has an unexpected or missing "
                        f"header and appears corrupted. Starting with an empty record set."
                    )

                    return []

                # Prepares rows to be processed, skipping header row
                for row_number, row in enumerate(
                    reader, start=2
                ):  # row 1 is the header
                    try:
                        # Process the row using the subclass's implementation
                        row = self._process_data_row(row)

                        if row is not None:
                            records.append(row)

                    # Logs error and skip corrupt rows
                    except (ValueError, KeyError, json.JSONDecodeError) as row_error:
                        self._log(
                            f"[Data Manager] Warning: skipping corrupt row {row_number} "
                            f"in '{self.__filepath}' ({row_error})."
                        )

                        continue

        # Logs errors and create an empty list
        except (csv.Error, OSError, UnicodeDecodeError) as file_error:
            self._log(
                f"[Data Manager] Warning: could not read '{self.__filepath}' ({file_error}). "
                f"Treating it as empty/corrupt and starting fresh."
            )

            return []

        self._log(
            f"[Data Manager] Loaded {len(records)} record(s) from '{self.__filepath}'."
        )

        return records

    def _log(self, message) -> None:
        """Logs a message if a logger is provided."""
        if self.__logger:
            self.__logger(message)

    def query(self, filter_fn) -> list:
        """
        Accepts a filter function and returns all matching records.
        Example: query(lambda r: r["outcome"] == "accept")
        """
        return [record for record in self.load() if filter_fn(record)]

    @abstractmethod
    def _process_data_row(self, row) -> dict:
        """Process a single row of data. This method should be implemented by subclasses to handle specific data formats.
        Args:
            row (dict): A dictionary representing a single row of data from the CSV file."""
        pass
