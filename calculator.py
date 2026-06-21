"""
Menu-driven calculator with history, error logging, and analysis reporting.

Run:
    python calculator.py
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import datetime
from pathlib import Path


class CalculatorError(Exception):
    """Base class for all custom calculator exceptions."""


class InvalidNumberError(CalculatorError):
    """Raised when a user enters a value that cannot be used as a number."""


class InvalidMenuChoiceError(CalculatorError):
    """Raised when a user selects an unavailable menu option."""


class InvalidOperationError(CalculatorError):
    """Raised when a user selects an unavailable arithmetic operation."""


class DivisionByZeroError(CalculatorError):
    """Raised when a user tries to divide by zero."""


class Calculator:
    """Performs arithmetic operations."""

    @staticmethod
    def add(first_number: float, second_number: float) -> float:
        return first_number + second_number

    @staticmethod
    def subtract(first_number: float, second_number: float) -> float:
        return first_number - second_number

    @staticmethod
    def multiply(first_number: float, second_number: float) -> float:
        return first_number * second_number

    @staticmethod
    def divide(first_number: float, second_number: float) -> float:
        if second_number == 0:
            raise DivisionByZeroError("Division by zero is not allowed.")
        return first_number / second_number


class InputValidator:
    """Validates and converts user input."""

    @staticmethod
    def get_menu_choice(prompt: str, valid_choices: set[str]) -> str:
        user_input = input(prompt).strip()

        if user_input not in valid_choices:
            raise InvalidMenuChoiceError(
                f"Invalid choice '{user_input}'. Please choose one of: "
                f"{', '.join(sorted(valid_choices))}."
            )

        return user_input

    @staticmethod
    def get_number(prompt: str) -> float:
        user_input = input(prompt).strip()

        try:
            number = float(user_input)
        except ValueError as exc:
            raise InvalidNumberError(
                f"'{user_input}' is not a valid number."
            ) from exc
        else:
            return number
        finally:
            # This block intentionally demonstrates cleanup-style flow.
            # No resource cleanup is needed after reading console input.
            pass


class FileManager:
    """Handles reading from and writing to text files."""

    def __init__(self, history_file: Path, error_file: Path) -> None:
        self.history_file = history_file
        self.error_file = error_file
        self.history_file.touch(exist_ok=True)
        self.error_file.touch(exist_ok=True)

    def append_history(self, entry: str) -> None:
        with self.history_file.open("a", encoding="utf-8") as file:
            file.write(entry + "\n")

    def read_history(self) -> list[str]:
        return self._read_lines(self.history_file)

    def read_errors(self) -> list[str]:
        return self._read_lines(self.error_file)

    @staticmethod
    def _read_lines(file_path: Path) -> list[str]:
        try:
            with file_path.open("r", encoding="utf-8") as file:
                lines = [line.rstrip() for line in file if line.strip()]
        except FileNotFoundError:
            return []
        else:
            return lines
        finally:
            # The with statement closes files automatically.
            pass


class ErrorLogger:
    """Logs errors with timestamps using Python's logging module."""

    def __init__(self, error_file: Path) -> None:
        self.logger = logging.getLogger("calculator_error_logger")
        self.logger.setLevel(logging.ERROR)
        self.logger.propagate = False

        if not self.logger.handlers:
            handler = logging.FileHandler(error_file, encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_error(self, error: Exception) -> None:
        error_type = type(error).__name__
        self.logger.error("%s | %s", error_type, error)


class AnalysisReport:
    """Builds a small report from history and error log files."""

    def __init__(self, file_manager: FileManager) -> None:
        self.file_manager = file_manager

    def generate(self) -> dict[str, str | int]:
        history_entries = self.file_manager.read_history()
        error_entries = self.file_manager.read_errors()
        error_types = self._extract_error_types(error_entries)
        most_common_error = "No errors recorded"

        if error_types:
            most_common_error = Counter(error_types).most_common(1)[0][0]

        return {
            "total_successful_calculations": len(history_entries),
            "total_errors": len(error_entries),
            "most_common_error_type": most_common_error,
        }

    @staticmethod
    def _extract_error_types(error_entries: list[str]) -> list[str]:
        error_types: list[str] = []

        for entry in error_entries:
            parts = [part.strip() for part in entry.split("|")]
            if len(parts) >= 3:
                error_types.append(parts[2])

        return error_types


class CalculatorApplication:
    """Coordinates the menu, calculations, file storage, and reports."""

    OPERATIONS = {
        "1": ("Addition", "+"),
        "2": ("Subtraction", "-"),
        "3": ("Multiplication", "*"),
        "4": ("Division", "/"),
    }

    def __init__(self) -> None:
        base_directory = Path(__file__).resolve().parent
        history_file = base_directory / "calculation_history.txt"
        error_file = base_directory / "error_log.txt"

        self.calculator = Calculator()
        self.file_manager = FileManager(history_file, error_file)
        self.error_logger = ErrorLogger(error_file)
        self.analysis_report = AnalysisReport(self.file_manager)

    def run(self) -> None:
        print("\nAdvanced Calculator Management System")

        while True:
            self._display_main_menu()

            try:
                choice = InputValidator.get_menu_choice(
                    "Enter your choice: ", {"1", "2", "3", "4"}
                )
            except CalculatorError as error:
                self._handle_error(error)
            else:
                if choice == "1":
                    self.perform_calculation()
                elif choice == "2":
                    self.view_history()
                elif choice == "3":
                    self.view_error_report()
                elif choice == "4":
                    print("Thank you for using the calculator. Goodbye!")
                    break
            finally:
                print("-" * 50)

    @staticmethod
    def _display_main_menu() -> None:
        print("\nMain Menu")
        print("1. Perform calculations")
        print("2. View calculation history")
        print("3. View error report")
        print("4. Exit")

    def perform_calculation(self) -> None:
        self._display_operation_menu()

        try:
            operation_choice = InputValidator.get_menu_choice(
                "Choose operation: ", set(self.OPERATIONS)
            )
            first_number = InputValidator.get_number("Enter first number: ")
            second_number = InputValidator.get_number("Enter second number: ")
            result = self._calculate(operation_choice, first_number, second_number)
        except CalculatorError as error:
            self._handle_error(error)
        else:
            operation_name, symbol = self.OPERATIONS[operation_choice]
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            history_entry = (
                f"{timestamp} | {operation_name} | "
                f"{first_number:g} {symbol} {second_number:g} = {result:g}"
            )

            self.file_manager.append_history(history_entry)
            print(f"Result: {result:g}")
            print("Calculation saved successfully.")
        finally:
            print("Calculation process completed.")

    def _display_operation_menu(self) -> None:
        print("\nOperations")
        for key, (operation_name, _) in self.OPERATIONS.items():
            print(f"{key}. {operation_name}")

    def _calculate(
        self, operation_choice: str, first_number: float, second_number: float
    ) -> float:
        if operation_choice == "1":
            return self.calculator.add(first_number, second_number)
        if operation_choice == "2":
            return self.calculator.subtract(first_number, second_number)
        if operation_choice == "3":
            return self.calculator.multiply(first_number, second_number)
        if operation_choice == "4":
            return self.calculator.divide(first_number, second_number)

        raise InvalidOperationError(f"Unknown operation '{operation_choice}'.")

    def view_history(self) -> None:
        print("\nCalculation History")
        history_entries = self.file_manager.read_history()

        if not history_entries:
            print("No successful calculations found.")
            return

        for index, entry in enumerate(history_entries, start=1):
            print(f"{index}. {entry}")

    def view_error_report(self) -> None:
        print("\nError Report")
        error_entries = self.file_manager.read_errors()

        if not error_entries:
            print("No errors logged.")
        else:
            for index, entry in enumerate(error_entries, start=1):
                print(f"{index}. {entry}")

        self.display_analysis_report()

    def display_analysis_report(self) -> None:
        report = self.analysis_report.generate()

        print("\nAnalysis Report")
        print(
            "Total successful calculations: "
            f"{report['total_successful_calculations']}"
        )
        print(f"Total errors: {report['total_errors']}")
        print(f"Most common error type: {report['most_common_error_type']}")

    def _handle_error(self, error: Exception) -> None:
        print(f"Error: {error}")
        self.error_logger.log_error(error)
        print("The error has been saved in the error log.")


def main() -> None:
    app = CalculatorApplication()
    app.run()


if __name__ == "__main__":
    main()
