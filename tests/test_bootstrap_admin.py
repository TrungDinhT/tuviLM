from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import ANY, MagicMock, Mock, call

import pytest
from bson import ObjectId
from pymongo.errors import PyMongoError

from api.auth import bootstrap_admin


USER_ID = ObjectId("64b000000000000000000001")
EMAIL = "admin@example.test"
URI = "mongodb://operator:secret@localhost:27017"
ARGS = ["--email", "  ADMIN@EXAMPLE.TEST  "]


@pytest.fixture
def bootstrap_context(monkeypatch):
    users, sessions = Mock(), Mock()
    users.find.return_value.limit.return_value = [
        {"_id": USER_ID, "email": EMAIL, "role": "user"}
    ]
    users.update_one.return_value = SimpleNamespace(matched_count=1)
    sessions.delete_many.return_value = SimpleNamespace(deleted_count=2)
    client = MagicMock()
    client.__enter__.return_value = {"auth_test": {"user": users, "session": sessions}}
    factory = Mock(return_value=client)
    confirmation = Mock(return_value="  ADMIN@EXAMPLE.TEST  ")
    settings = SimpleNamespace(auth=SimpleNamespace(mongo_uri=URI, database_name="auth_test"))
    monkeypatch.setattr(bootstrap_admin, "MongoClient", factory)
    monkeypatch.setattr(bootstrap_admin, "get_settings", lambda: settings)
    monkeypatch.setattr("builtins.input", confirmation)
    writes = Mock()
    writes.attach_mock(sessions.delete_many, "revoke")
    writes.attach_mock(users.update_one, "promote")
    return SimpleNamespace(
        users=users, sessions=sessions, factory=factory, confirmation=confirmation, writes=writes
    )


def test_normalized_email_confirmation_revokes_sessions_before_role_only_update(
    bootstrap_context, capsys
):
    context = bootstrap_context
    bootstrap_admin.main(ARGS)

    context.factory.assert_called_once_with(URI, serverSelectionTimeoutMS=5000, w="majority")
    context.users.find.assert_called_once_with(
        {"email": EMAIL}, {"email": 1, "role": 1}
    )
    context.users.find.return_value.limit.assert_called_once_with(2)
    assert context.writes.mock_calls == [
        call.revoke({"userId": USER_ID}),
        call.promote(
            {"_id": USER_ID, "email": EMAIL, "role": "user"},
            {"$set": {"role": "admin", "updatedAt": ANY}},
        ),
    ]
    updated_at = context.users.update_one.call_args.args[1]["$set"]["updatedAt"]
    assert isinstance(updated_at, datetime) and updated_at.tzinfo is UTC
    output = capsys.readouterr().out
    assert "Revoked 2 sessions" in output and "secret" not in output

    context.users.update_one.return_value.matched_count = 0
    with pytest.raises(SystemExit, match="Account changed during confirmation"):
        bootstrap_admin.main(ARGS)
    assert "Administrator access granted" not in capsys.readouterr().out


def test_refused_confirmation_or_nonunique_account_never_writes(bootstrap_context):
    context = bootstrap_context
    user = {"_id": USER_ID, "email": EMAIL, "role": "user"}
    other = {**user, "_id": ObjectId("64b000000000000000000002")}
    for found, response, message in [
        ([user], "no", "Confirmation did not match"),
        ([user], "other@example.test", "Confirmation did not match"),
        ([], EMAIL, "No account matches"),
        ([user, other], EMAIL, "Multiple accounts match"),
    ]:
        context.users.find.return_value.limit.return_value = found
        context.confirmation.reset_mock()
        context.confirmation.return_value = response
        with pytest.raises(SystemExit, match=message):
            bootstrap_admin.main(ARGS)
        context.sessions.delete_many.assert_not_called()
        context.users.update_one.assert_not_called()
        if len(found) != 1:
            context.confirmation.assert_not_called()


def test_revocation_failure_never_promotes_and_hides_database_details(bootstrap_context):
    context = bootstrap_context
    context.sessions.delete_many.side_effect = PyMongoError(f"Connection failed: {URI}")
    with pytest.raises(SystemExit) as error:
        bootstrap_admin.main(ARGS)

    context.sessions.delete_many.assert_called_once_with({"userId": USER_ID})
    context.users.update_one.assert_not_called()
    assert str(error.value) == (
        "Database operation failed. Check the account role before retrying."
    )
    assert error.value.__suppress_context__
