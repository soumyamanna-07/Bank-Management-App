# Bank-Management-App
Python bank management system with a Streamlit web interface and JSON-backed storage.  Console and web-based bank account manager built in Python and Streamlit.  Bank management system supporting account creation, deposits, withdrawals, updates, and closure — CLI and Streamlit interfaces.

## How it works

`Bank` loads `data.json` into memory on startup and writes it back after every change. The file path is anchored to the script's own folder with `Path(__file__).parent`, so the app finds its data no matter which directory you launch it from.

Every rule violation raises `BankError` with a message written for the user. The interface catches it and shows it as an error, which keeps validation in one place instead of scattered through the UI.

Account numbers are three uppercase letters and four digits, shuffled together, and checked against existing accounts so no two people can be issued the same one.

PINs are stored as strings rather than integers. Storing `0123` as an integer silently turns it into `123`, which then fails a 4-digit length check — a bug worth avoiding.

Older records that used the key `accountNo.` or stored the PIN as a number are upgraded automatically when the file loads, so existing data keeps working.

## Rules

| Rule | Value |
|---|---|
| Minimum age | 18 |
| PIN length | 4 digits |
| Maximum single deposit | 10,000 |
| Withdrawal | Cannot exceed balance |

## A note on security

PINs are stored in plain text in `data.json`. That is fine for a learning project but would not be acceptable in production — a real system would store a salted hash and compare hashes at sign-in. `data.json` is listed in `.gitignore` so account data never reaches the repository.

## Built with

Python, Streamlit, and the standard library (`json`, `pathlib`, `random`, `string`).
