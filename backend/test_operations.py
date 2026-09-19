import contextlib
import hashlib
import io
import os
import stat
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.test import SimpleTestCase

from scripts.database import main


class DatabaseCommandTests(SimpleTestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.backup = Path(self.directory.name) / "backup.dump"
        self.checksum = self.backup.with_suffix(".dump.sha256")
        self.enterContext(
            patch.dict(os.environ, {"DATABASE_URL": "postgresql://reader@localhost/source"})
        )
        self.enterContext(contextlib.redirect_stdout(io.StringIO()))

    def command(self, *args):
        with patch("sys.argv", ["database.py", *args]):
            main()

    def test_backup_is_private_has_matching_checksum_and_cannot_be_overwritten(self):
        content = b"synthetic database dump\n" * 10000

        def dump(*args, **kwargs):
            kwargs["stdout"].write(content)

        with patch("scripts.database.subprocess.run", side_effect=dump):
            self.command("backup", str(self.backup))
        self.assertEqual(self.backup.read_bytes(), content)
        self.assertEqual(self.checksum.read_text().strip(), hashlib.sha256(content).hexdigest())
        for file in (self.backup, self.checksum):
            self.assertEqual(stat.S_IMODE(file.stat().st_mode), 0o600)
        with patch("scripts.database.subprocess.run") as run:
            with self.assertRaises(FileExistsError):
                self.command("backup", str(self.backup))
            run.assert_not_called()

    def test_restore_rejects_modified_backup_before_creating_database(self):
        self.backup.write_bytes(b"modified")
        self.checksum.write_text(hashlib.sha256(b"original").hexdigest())
        with patch("scripts.database.subprocess.run") as run:
            with self.assertRaisesRegex(SystemExit, "checksum mismatch"):
                self.command("restore", str(self.backup), "--new-database", "restored")
            run.assert_not_called()

    def test_restore_refuses_source_database(self):
        with patch("scripts.database.subprocess.run") as run:
            with self.assertRaisesRegex(SystemExit, "source database"):
                self.command("restore", str(self.backup), "--new-database", "source")
            run.assert_not_called()

    def test_release_checks_public_url_before_calling_docker(self):
        # An empty PATH makes accidental deployment commands fail without touching services.
        result = subprocess.run(
            ["/bin/bash", str(settings.BASE_DIR / "scripts/release.sh"), "deploy"],
            env={"PATH": ""},
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Export DJANGO_PUBLIC_URL", result.stderr)
        self.assertNotIn("docker", result.stderr)
