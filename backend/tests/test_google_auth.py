import unittest
from autocare.accounts import Accounts, Invalid
from fixtures import TEST_SETTINGS, build


class TestGoogleAuth(unittest.TestCase):
    def setUp(self):
        self.svc, self.llm, self.db = build()
        self.accounts = Accounts(self.db, TEST_SETTINGS)

    def test_google_auto_registration(self):
        user = self.accounts.authenticate_or_register_google(
            email="talhabhattiak47@gmail.com",
            full_name="Talha Ali Bhatti"
        )
        self.assertEqual(user["email"], "talhabhattiak47@gmail.com")
        self.assertEqual(user["full_name"], "Talha Ali Bhatti")
        self.assertEqual(user["role"], "owner")
        self.assertTrue(user["user_id"])

    def test_google_login_existing_user(self):
        u1 = self.accounts.authenticate_or_register_google(
            email="existing.google@autocare.pk",
            full_name="Google Tester"
        )
        u2 = self.accounts.authenticate_or_register_google(
            email="existing.google@autocare.pk",
            full_name="Google Tester Different Name"
        )
        self.assertEqual(u1["user_id"], u2["user_id"])
        self.assertEqual(u2["full_name"], "Google Tester")

    def test_google_invalid_email_refused(self):
        with self.assertRaises(Invalid):
            self.accounts.authenticate_or_register_google(email="not-an-email")


if __name__ == "__main__":
    unittest.main()
