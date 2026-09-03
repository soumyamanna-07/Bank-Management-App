"""Core banking logic.

This module never calls print() or input(). It raises BankError when a rule is
broken, and the interface layer (app.py) decides how to show that to the user.
Keeping the two apart means the same logic can run behind Streamlit, a terminal
menu, or a test suite without any changes.
"""

from __future__ import annotations

import json
import random
import string
from pathlib import Path

# Anchored to this file, not to the folder the terminal happens to be in.
DATABASE = Path(__file__).parent / "data.json"

MIN_AGE = 18
PIN_LENGTH = 4
MAX_DEPOSIT = 10_000


class BankError(Exception):
    """Raised when an operation fails a validation rule."""


class Bank:
    def __init__(self, database: Path | str = DATABASE) -> None:
        self.database = Path(database)
        self.data: list[dict] = self._load()

    # ------------------------------------------------------------------ storage

    def _load(self) -> list[dict]:
        """Read the account file. A missing or empty file means no accounts yet."""
        if not self.database.exists():
            return []

        try:
            text = self.database.read_text(encoding="utf-8").strip()
        except OSError as err:
            raise BankError(f"Could not read {self.database.name}: {err}") from err

        if not text:
            return []

        try:
            records = json.loads(text)
        except json.JSONDecodeError as err:
            raise BankError(
                f"{self.database.name} is not valid JSON. Fix or delete it. ({err})"
            ) from err

        if not isinstance(records, list):
            raise BankError(f"{self.database.name} should contain a list of accounts.")

        return self._migrate(records)

    @staticmethod
    def _migrate(records: list[dict]) -> list[dict]:
        """Bring older records up to the current shape so existing data still works."""
        for record in records:
            if "accountNo." in record:
                record["accountNo"] = record.pop("accountNo.")
            # PINs are stored as text so a PIN like 0123 keeps its leading zero.
            record["pin"] = str(record.get("pin", "")).zfill(PIN_LENGTH)
            record["balance"] = float(record.get("balance", 0))
        return records

    def _save(self) -> None:
        self.database.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # --------------------------------------------------------------- validation

    @staticmethod
    def _clean_pin(pin: str) -> str:
        pin = str(pin).strip()
        if len(pin) != PIN_LENGTH or not pin.isdigit():
            raise BankError(f"The PIN must be exactly {PIN_LENGTH} digits.")
        return pin

    @staticmethod
    def _clean_email(email: str) -> str:
        email = email.strip()
        head, _, tail = email.partition("@")
        if not head or "." not in tail or tail.endswith("."):
            raise BankError("That email address does not look right.")
        return email

    def _new_account_number(self) -> str:
        """Three letters and four digits, shuffled, and checked against existing ones."""
        taken = {record["accountNo"] for record in self.data}
        while True:
            characters = random.choices(string.ascii_uppercase, k=3)
            characters += random.choices(string.digits, k=4)
            random.shuffle(characters)
            number = "".join(characters)
            if number not in taken:
                return number

    # --------------------------------------------------------------- operations

    def create_account(self, name: str, age: int, email: str, pin: str) -> dict:
        name = name.strip()
        if not name:
            raise BankError("Enter your name.")
        if age < MIN_AGE:
            raise BankError(f"You have to be at least {MIN_AGE} to open an account.")

        record = {
            "name": name,
            "age": int(age),
            "email": self._clean_email(email),
            "pin": self._clean_pin(pin),
            "accountNo": self._new_account_number(),
            "balance": 0.0,
        }
        self.data.append(record)
        self._save()
        return record

    def find(self, account_no: str, pin: str) -> dict | None:
        """Return the matching account, or None. Never raises."""
        account_no = str(account_no).strip().upper()
        pin = str(pin).strip()
        for record in self.data:
            if record["accountNo"] == account_no and record["pin"] == pin:
                return record
        return None

    def authenticate(self, account_no: str, pin: str) -> dict:
        """Same as find(), but raises instead of returning None."""
        record = self.find(account_no, pin)
        if record is None:
            raise BankError("No account matches that number and PIN.")
        return record

    def deposit(self, account_no: str, pin: str, amount: float) -> float:
        record = self.authenticate(account_no, pin)
        if amount <= 0:
            raise BankError("Enter an amount greater than 0.")
        if amount > MAX_DEPOSIT:
            raise BankError(f"The most you can deposit at once is {MAX_DEPOSIT:,}.")

        record["balance"] = round(record["balance"] + amount, 2)
        self._save()
        return record["balance"]

    def withdraw(self, account_no: str, pin: str, amount: float) -> float:
        record = self.authenticate(account_no, pin)
        if amount <= 0:
            raise BankError("Enter an amount greater than 0.")
        if amount > record["balance"]:
            raise BankError("That is more than your balance.")

        record["balance"] = round(record["balance"] - amount, 2)
        self._save()
        return record["balance"]

    def update_details(
        self,
        account_no: str,
        pin: str,
        name: str = "",
        email: str = "",
        new_pin: str = "",
    ) -> dict:
        """Only the fields you actually fill in are changed."""
        record = self.authenticate(account_no, pin)

        if name.strip():
            record["name"] = name.strip()
        if email.strip():
            record["email"] = self._clean_email(email)
        if new_pin.strip():
            record["pin"] = self._clean_pin(new_pin)

        self._save()
        return record

    def close_account(self, account_no: str, pin: str) -> dict:
        record = self.authenticate(account_no, pin)
        self.data.remove(record)
        self._save()
        return record
