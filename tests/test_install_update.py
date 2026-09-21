"""Offline smoke tests for the Bash installer and updater (Linux + Git)."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = Path('.agents/skills/flatplanet-orchestrator')


class InstallUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='flatplanet tests ')
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'source checkout'
        self.app = self.base / 'application repo'
        self.state = self.base / 'state'
        self.env = os.environ.copy()
        for key in list(self.env):
            if key.startswith('GIT_'):
                self.env.pop(key)
        self.env.update(HOME=str(self.base), XDG_STATE_HOME=str(self.state),
                        GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull)
        for repo in (self.source, self.app):
            repo.mkdir()
            self.git(repo, 'init', '-q')
            self.git(repo, 'config', 'user.name', 'Installer Test')
            self.git(repo, 'config', 'user.email', 'test@example.invalid')
        (self.source / 'scripts').mkdir()
        for name in ('install.sh', 'update.sh'):
            shutil.copy2(ROOT / 'scripts' / name, self.source / 'scripts' / name)
        (self.source / SKILL).mkdir(parents=True)
        (self.source / SKILL / 'SKILL.md').write_text('name: flatplanet-orchestrator\nversion one\n')
        self.git(self.source, 'add', '.')
        self.git(self.source, 'commit', '-qm', 'Source fixture')
        for name, text in {
            'AGENTS.md': 'Application rules\n',
            '.codex/config.toml': 'model = "keep-this"\n',
            '.agents/skills/another/SKILL.md': 'Other skill\n',
        }.items():
            file = self.app / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(text)
        self.git(self.app, 'add', '.')
        self.git(self.app, 'commit', '-qm', 'Application fixture')
        self.original_head = self.git(self.app, 'rev-parse', 'HEAD').stdout

    def git(self, repo, *args):
        return subprocess.run(['git', '-C', str(repo), *args], env=self.env,
                              capture_output=True, text=True, check=True, timeout=10)

    def run_script(self, script='install.sh', *args, cwd=None, env=None):
        return subprocess.run(['bash', str(self.source / 'scripts' / script), *map(str, args)],
                              cwd=cwd or self.app, env=env or self.env,
                              capture_output=True, text=True, timeout=10)

    def install(self):
        result = self.run_script('install.sh', self.app)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def backup_paths(self):
        return sorted(self.state.glob('flatplanet-orchestrator/backups/update.*/flatplanet-orchestrator'))

    def assert_unrelated_unchanged(self):
        self.assertEqual((self.app / 'AGENTS.md').read_text(), 'Application rules\n')
        self.assertEqual((self.app / '.codex/config.toml').read_text(), 'model = "keep-this"\n')
        self.assertEqual((self.app / '.agents/skills/another/SKILL.md').read_text(), 'Other skill\n')
        self.assertEqual(self.git(self.app, 'rev-parse', 'HEAD').stdout, self.original_head)
        self.assertEqual(self.git(self.app, 'diff', '--cached', '--name-only').stdout, '')
        self.assertFalse((self.app / '.git/flatplanet-orchestrator-install.lock').exists())

    def test_install_from_nested_cwd_with_spaces(self):
        nested = self.app / 'src' / 'deep'
        nested.mkdir(parents=True)
        result = self.run_script(cwd=nested)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.app / SKILL / 'SKILL.md').read_bytes(),
                         (self.source / SKILL / 'SKILL.md').read_bytes())
        self.assertIn(self.git(self.source, 'rev-parse', 'HEAD').stdout.strip(), result.stdout)
        self.assert_unrelated_unchanged()

    def test_install_refuses_existing_installation(self):
        self.install()
        (self.app / SKILL / 'SKILL.md').write_text('Local edits\n')
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Already installed', result.stderr)
        self.assertEqual((self.app / SKILL / 'SKILL.md').read_text(), 'Local edits\n')

    def test_update_replaces_files_preserves_local_files_and_backs_up(self):
        self.install()
        (self.app / SKILL / 'SKILL.md').write_text('Local customization\n')
        (self.app / SKILL / 'local-only.txt').write_text('Keep me\n')
        (self.source / SKILL / 'SKILL.md').write_text('Version two\n')
        (self.source / SKILL / 'references').mkdir()
        (self.source / SKILL / 'references/new.md').write_text('New reference\n')
        result = self.run_script('update.sh', self.app)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.app / SKILL / 'SKILL.md').read_text(), 'Version two\n')
        self.assertEqual((self.app / SKILL / 'local-only.txt').read_text(), 'Keep me\n')
        self.assertEqual((self.app / SKILL / 'references/new.md').read_text(), 'New reference\n')
        backups = self.backup_paths()
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / 'SKILL.md').read_text(), 'Local customization\n')
        self.assertEqual((backups[0] / 'local-only.txt').read_text(), 'Keep me\n')
        self.assertIn('local skill changes', result.stdout)
        self.assert_unrelated_unchanged()

    def test_repeated_updates_keep_distinct_backups(self):
        self.install()
        for _ in range(2):
            result = self.run_script('update.sh')
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.backup_paths()), 2)
        self.assert_unrelated_unchanged()

    def test_update_requires_installation(self):
        result = self.run_script('update.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.app / SKILL).exists())

    def test_missing_and_non_git_targets_are_rejected(self):
        non_git = self.base / 'not a repo'
        non_git.mkdir()
        for target in (self.base / 'missing', non_git):
            result = self.run_script('install.sh', target)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((target / SKILL).exists())

    def test_self_install_is_rejected(self):
        result = self.run_script('update.sh', self.source)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('not this source checkout', result.stderr)

    def test_parent_symlinks_are_rejected(self):
        for relative in (Path('.agents'), Path('.agents/skills')):
            with self.subTest(relative=relative):
                original = self.app / relative
                relocated = self.base / 'linked directory'
                original.rename(relocated)
                original.symlink_to(relocated, target_is_directory=True)
                try:
                    result = self.run_script()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('Symlinked', result.stderr)
                finally:
                    original.unlink()
                    relocated.rename(original)
        self.assert_unrelated_unchanged()

    def test_update_rejects_symlinks_inside_installation(self):
        self.install()
        file = self.app / SKILL / 'SKILL.md'
        file.unlink()
        file.symlink_to(self.app / 'AGENTS.md')
        result = self.run_script('update.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.backup_paths(), [])
        self.assert_unrelated_unchanged()

    def test_update_does_not_mutate_external_hardlink(self):
        self.install()
        file = self.app / SKILL / 'SKILL.md'
        file.unlink()
        file.hardlink_to(self.app / 'AGENTS.md')
        result = self.run_script('update.sh')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_unrelated_unchanged()

    def test_unsafe_source_is_rejected(self):
        bad = self.source / SKILL / 'linked.md'
        bad.symlink_to(self.app / 'AGENTS.md')
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.app / SKILL).exists())

    def test_type_conflict_is_rejected_before_changes(self):
        self.install()
        (self.source / SKILL / 'helper').write_text('Upstream file\n')
        (self.app / SKILL / 'helper').mkdir()
        result = self.run_script('update.sh')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('File/directory conflict', result.stderr)
        self.assertEqual(self.backup_paths(), [])
        self.assertTrue((self.app / SKILL / 'helper').is_dir())

    def test_empty_source_skill_is_rejected(self):
        (self.source / SKILL / 'SKILL.md').write_text('')
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.app / SKILL).exists())

    def test_backup_inside_repository_is_rejected(self):
        self.install()
        result = self.run_script('update.sh', env={**self.env, 'XDG_STATE_HOME': str(self.app / '.agents')})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('outside both repositories', result.stderr)
        self.assert_unrelated_unchanged()

    def test_failed_copy_keeps_backup_and_releases_lock(self):
        self.install()
        (self.app / SKILL / 'SKILL.md').write_text('Recoverable edits\n')
        bin_dir = self.base / 'fake bin'
        bin_dir.mkdir()
        fake_cp = bin_dir / 'cp'
        fake_cp.write_text('#!/usr/bin/env bash\n'
                           'for arg; do [[ "$arg" != --remove-destination ]] || exit 42; done\n'
                           f'exec "{shutil.which("cp")}" "$@"\n')
        fake_cp.chmod(0o755)
        result = self.run_script('update.sh', env={**self.env, 'PATH': f'{bin_dir}:{self.env["PATH"]}'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Full backup:', result.stderr)
        self.assertEqual((self.backup_paths()[0] / 'SKILL.md').read_text(), 'Recoverable edits\n')
        self.assert_unrelated_unchanged()

    def test_lock_conflict_does_not_remove_other_lock(self):
        lock = self.app / '.git/flatplanet-orchestrator-install.lock'
        lock.mkdir()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(lock.is_dir())
        self.assertFalse((self.app / SKILL).exists())

    def test_help_and_bad_arguments(self):
        for script in ('install.sh', 'update.sh'):
            self.assertEqual(self.run_script(script, '--help').returncode, 0)
            self.assertNotEqual(self.run_script(script, '--bad-option').returncode, 0)
            self.assertNotEqual(self.run_script(script, self.app, self.app).returncode, 0)


if __name__ == '__main__':
    unittest.main()
