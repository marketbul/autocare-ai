"""Create an account from the command line, e.g. the first admin.

  python -m ingest.create_user --role admin --name "Ahmad Zahid" --email you@example.com

You'll be asked for the password (it is not shown or stored in your command history).
Owners can also sign up in the app; mechanics and admins are created here or promoted
by an admin on the Users screen.
"""
from __future__ import annotations

import argparse
import getpass


def main() -> None:
    from autocare.accounts import Accounts, Invalid
    from autocare.auth import ROLES
    from autocare.config import load_settings
    from autocare.db import Database

    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--role", choices=ROLES, required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--email", required=True)
    a = ap.parse_args()

    pw = getpass.getpass("Password (min 8 characters): ")
    if pw != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords don't match.")
    s = load_settings()
    db = Database(s.database_url)
    db.create_schema()
    try:
        u = Accounts(db, s).create_user(a.name, a.email, pw, a.role)
    except Invalid as e:
        raise SystemExit(str(e))
    print(f"Created {u['role']} account for {u['email']}.")


if __name__ == "__main__":
    main()
