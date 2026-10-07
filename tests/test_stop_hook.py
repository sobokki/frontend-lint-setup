"""Exercise the hook with real Git state and a stub ESLint launcher."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HOOK = Path(__file__).resolve().parents[1] / 'assets/frontend-lint-stop.sh'


class StopHookTests(unittest.TestCase):
    mode = '--claude'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Hook Test')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'core.hooksPath', str(self.root / 'no-hooks'))
        (self.root / 'frontend').mkdir()
        (self.root / 'frontend/base.ts').write_text('export {};\n')
        self.git('add', '.')
        self.git('commit', '-qm', 'fixture')
        bin_dir = self.root / 'test-bin'
        bin_dir.mkdir()
        stub = bin_dir / 'npx'
        stub.write_text('#!/usr/bin/env python3\nimport json,os,sys\n'
                        'from pathlib import Path\n'
                        'Path(os.environ["HOOK_ARGS"]).write_text(json.dumps(sys.argv[1:]))\n'
                        'sys.exit(int(os.environ.get("LINT_EXIT", "0")))\n')
        stub.chmod(0o755)
        self.env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ['PATH'],
                        HOOK_ARGS=str(self.root / 'args.json'), CLAUDE_PROJECT_DIR=str(self.root))

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def run_hook(self, payload='{}', code=0, cwd=None):
        if self.mode == '--codex':
            try:
                data = json.loads(payload)
                if isinstance(data, dict):
                    data.setdefault('cwd', str(self.root))
                    payload = json.dumps(data)
            except ValueError:
                pass
        result = subprocess.run(['/bin/bash', str(HOOK), self.mode], cwd=cwd or self.root,
                                env=dict(self.env, LINT_EXIT=str(code)),
                                input=payload, text=True, capture_output=True)
        path = self.root / 'args.json'
        args = json.loads(path.read_text()) if path.exists() else None
        if self.mode == '--codex' and result.returncode == 0:
            self.assertEqual(json.loads(result.stdout), {})
        return result, args

    def test_clean(self):
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(args)

    def test_failure_blocks(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        result, args = self.run_hook(code=1)
        self.assertEqual(result.returncode, 2)
        self.assertIn('./base.ts', args)
        self.assertIn('ESLint', result.stderr)

    def test_loop_guard(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        result, args = self.run_hook('{"stop_hook_active":true}', code=1)
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(args)

    def test_untracked_unicode_and_spaces(self):
        name = '한글 이름.tsx'
        (self.root / 'frontend' / name).write_text('export {};\n')
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIsNotNone(args)
        self.assertIn('./' + name, args)

    def test_staged_before_first_commit(self):
        self.git('checkout', '--orphan', 'unborn')
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIsNotNone(args)
        self.assertIn('./base.ts', args)

    def test_staged_then_deleted(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        self.git('add', 'frontend/base.ts')
        (self.root / 'frontend/base.ts').unlink()
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(args)

    def test_staged_and_unstaged_file_once(self):
        path = self.root / 'frontend/base.ts'
        path.write_text('staged\n')
        self.git('add', 'frontend/base.ts')
        path.write_text('unstaged\n')
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertEqual(args.count('./base.ts'), 1)

    def test_unusual_names(self):
        names = ['line\nbreak.ts', '-option.ts', 'module.mts', 'module.cts']
        for name in names:
            (self.root / 'frontend' / name).write_text('export {};\n')
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        for name in names:
            self.assertIn('./' + name, args)

    def test_non_frontend_change(self):
        (self.root / 'backend.ts').write_text('changed\n')
        result, args = self.run_hook()
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(args)

    def test_loop_guard_json_whitespace(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        result, args = self.run_hook('{"stop_hook_active" : true}', code=1)
        self.assertEqual(result.returncode, 0)
        self.assertIsNone(args)

    def test_project_root_with_different_cwd(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        self.env['CLAUDE_PROJECT_DIR'] = str(self.root)
        with tempfile.TemporaryDirectory() as elsewhere:
            result, args = self.run_hook(code=1, cwd=elsewhere)
        self.assertEqual(result.returncode, 2)
        self.assertIn('./base.ts', args)

    def test_invalid_json(self):
        result, args = self.run_hook('{broken')
        self.assertEqual(result.returncode, 2)
        self.assertIsNone(args)

    def test_nested_true_does_not_skip(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        result, args = self.run_hook('{"metadata":{"stop_hook_active":true},"stop_hook_active":false}', code=1)
        self.assertEqual(result.returncode, 2)
        self.assertIsNotNone(args)


class CodexStopHookTests(StopHookTests):
    mode = '--codex'

    def test_payload_cwd_overrides_claude_environment(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        with tempfile.TemporaryDirectory() as elsewhere:
            self.env['CLAUDE_PROJECT_DIR'] = elsewhere
            result, args = self.run_hook(code=1, cwd=elsewhere)
        self.assertEqual(result.returncode, 2)
        self.assertIn('./base.ts', args)
        self.assertEqual(result.stdout, '')

    def test_invalid_cwd(self):
        result, args = self.run_hook('{"cwd":null}')
        self.assertEqual(result.returncode, 2)
        self.assertIn('cwd', result.stderr)
        self.assertIsNone(args)

    def test_missing_cwd(self):
        result = subprocess.run(['/bin/bash', str(HOOK), '--codex'], cwd=self.root,
                                env=self.env, input='{}', text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('cwd', result.stderr)

    def test_lint_configuration_failure(self):
        (self.root / 'frontend/base.ts').write_text('changed\n')
        result, args = self.run_hook(code=2)
        self.assertEqual(result.returncode, 2)
        self.assertIsNotNone(args)
        self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
