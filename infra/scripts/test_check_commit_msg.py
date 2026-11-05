"""Tests du vérificateur de messages de commit. Lancement : python3 -m unittest discover infra/scripts"""

import unittest

from check_commit_msg import check


class CheckCommitMsgTest(unittest.TestCase):
    def test_valid_messages(self) -> None:
        for message in (
            "[ADD] api: endpoint POST /meals/analyze (#23)",
            "[FIX] mobile: jauge négative après suppression d'un repas (#57)",
            "[SECU] api: contrôle d'appartenance sur GET /meals/{id} (#31)",
            "[MERGE] develop dans main pour v0.2.0",
            "[CONFIG] ci: pipeline lint (#5)\n\nCorps du message.\n",
            "# commentaire Git\n[DOCS] docs: guide d'installation (#3)",
        ):
            with self.subTest(message=message):
                self.assertEqual(check(message), [])

    def test_git_generated_messages_are_accepted(self) -> None:
        for message in (
            "Merge branch 'develop' into feature/4-x",
            'Revert "[ADD] api: x (#4)"',
            "fixup! [ADD] api: x (#4)",
        ):
            with self.subTest(message=message):
                self.assertEqual(check(message), [])

    def test_invalid_format(self) -> None:
        for message in (
            "fix bug",
            "[add] api: minuscules (#1)",
            "[ADD] API: portée en majuscules (#1)",
            "[ADD] backend: portée inconnue (#1)",
            "[WIP] api: tag inconnu (#1)",
            "ADD api: sans crochets (#1)",
            "",
        ):
            with self.subTest(message=message):
                self.assertNotEqual(check(message), [])

    def test_scope_required_except_merge_and_release(self) -> None:
        errors = check("[ADD] endpoint d'analyse (#1)")
        self.assertTrue(any("Portée manquante" in e for e in errors))
        self.assertEqual(check("[RELEASE] version 1.0.0 (#61)"), [])

    def test_issue_reference_required(self) -> None:
        errors = check("[ADD] api: endpoint d'analyse")
        self.assertTrue(any("référence d'issue" in e for e in errors))

    def test_too_long(self) -> None:
        errors = check("[ADD] api: " + "x" * 70 + " (#1)")
        self.assertTrue(any("trop longue" in e for e in errors))

    def test_trailing_period(self) -> None:
        errors = check("[ADD] api: endpoint d'analyse. (#1)")
        self.assertTrue(any("point final" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
