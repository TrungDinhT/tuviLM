from __future__ import annotations

import argparse
from datetime import UTC, datetime

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from api.settings import get_settings


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Grant administrator access to an existing Better Auth account."
    )
    parser.add_argument("--email", required=True, help="The email registered to the account.")
    args = parser.parse_args(argv)
    email = args.email.strip().lower()
    if not email:
        parser.error("--email must not be empty.")

    settings = get_settings().auth
    try:
        with MongoClient(
            settings.mongo_uri, serverSelectionTimeoutMS=5000, w="majority"
        ) as client:
            database = client[settings.database_name]
            users = list(
                database["user"].find({"email": email}, {"email": 1, "role": 1}).limit(2)
            )
            if not users:
                raise SystemExit("No account matches this email. Register first.")
            if len(users) > 1:
                raise SystemExit("Multiple accounts match this email. Nothing changed.")
            user = users[0]
            user_id = user["_id"]
            if not isinstance(user_id, ObjectId):
                raise SystemExit("Unexpected account ID. Nothing changed.")
            if user.get("role") == "admin":
                print("This account is already an administrator. Nothing changed.")
                return
            if user.get("role", "user") != "user":
                raise SystemExit("Unexpected account role. Nothing changed.")

            print(f"Database: {settings.database_name}")
            print(f"Account: {user['email']} ({user_id})")
            try:
                confirmation = input(
                    "Type the email above to grant administrator access: "
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                raise SystemExit("Cancelled. Nothing changed.") from None
            if confirmation != email:
                raise SystemExit("Confirmation did not match. Nothing changed.")

            revoked = database["session"].delete_many({"userId": user_id})
            expected_role = user["role"] if "role" in user else {"$exists": False}
            updated = database["user"].update_one(
                {"_id": user_id, "email": email, "role": expected_role},
                {"$set": {"role": "admin", "updatedAt": datetime.now(UTC)}},
            )
            if updated.matched_count != 1:
                raise SystemExit("Account changed during confirmation. Check its role before retrying.")
            print(f"Administrator access granted. Revoked {revoked.deleted_count} sessions.")
            print("Sign in again, then open /admin/redeem-codes.")
    except PyMongoError:
        raise SystemExit(
            "Database operation failed. Check the account role before retrying."
        ) from None
    except KeyboardInterrupt:
        raise SystemExit("Interrupted. Check the account role before retrying.") from None


if __name__ == "__main__":
    main()
