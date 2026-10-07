"""Optional integration checks against real, separately installed npm packages.

Set FRONTEND_LINT_NODE_MODULES to the absolute node_modules path.
"""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULES = os.environ.get('FRONTEND_LINT_NODE_MODULES')


@unittest.skipUnless(MODULES, 'Set FRONTEND_LINT_NODE_MODULES for real ESLint checks')
class ExampleTests(unittest.TestCase):
    def test_documented_configs(self):
        snippets = re.findall(r'```js\n(.*?)\n```', (ROOT / 'SKILL.md').read_text(), re.S)
        self.assertEqual(len(snippets), 2)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            (root / 'node_modules').symlink_to(Path(MODULES).resolve(), target_is_directory=True)
            (root / 'package.json').write_text('{"private":true,"type":"module"}')
            (root / 'pages').mkdir()
            # Follow the documented JavaScript-only conversion, then execute it.
            next_js = snippets[0].replace('import nextTs from "eslint-config-next/typescript";\n', '').replace('  ...nextTs,\n', '')
            next_js = re.sub(r'      "@typescript-eslint/consistent-type-imports": \[.*?      \],\n', '', next_js, flags=re.S)
            next_js = next_js.replace('      "@typescript-eslint/no-unused-vars": "off",\n', '')
            vite_js = snippets[1].replace('import tseslint from "typescript-eslint";\n', '')
            vite_js = re.sub(r'  \.\.\.tseslint\.configs\.recommended\.map\(.*?  \}\)\),\n', '', vite_js, flags=re.S | re.M)
            vite_js = re.sub(r'^  \{\n    files: \["\*\*/\*\.\{ts,tsx,mts,cts\}"\],\n    rules: \{.*?^  \},\n', '', vite_js, flags=re.S | re.M)
            react_js = vite_js.replace('import reactRefresh from "eslint-plugin-react-refresh"; // Vite 전용 (HMR)\n', '')
            react_js = react_js.replace('      "react-refresh": reactRefresh,\n', '').replace('      "react-refresh/only-export-components": "warn",\n', '')
            variants = [('next', snippets[0]), ('vite', snippets[1]), ('next-js', next_js), ('vite-js', vite_js), ('react-js', react_js)]
            for framework, snippet in variants:
                (root / 'eslint.config.mjs').write_text(snippet)
                extensions = ('js', 'jsx', 'mjs', 'cjs') if framework.endswith('-js') else ('tsx', 'jsx', 'mts', 'cts')
                for extension in extensions:
                    with self.subTest(framework=framework, extension=extension):
                        source = root / 'pages' / ('App.' + extension)
                        source.write_text('export default function App() {\n'
                                          'return <button onClick={() => window.alert("hi")}>Hi</button>;\n}\n')
                        if extension in ('mts', 'cts', 'mjs', 'cjs'):
                            source.write_text('export const value = 1;\n')
                        if extension == 'cjs':
                            source.write_text('exports.value = 1;\n')
                        def lint():
                            return subprocess.run(
                                ['node', str(root / 'node_modules/eslint/bin/eslint.js'),
                                 '--format', 'json', str(source)], cwd=root,
                                capture_output=True, text=True)
                        result = lint()
                        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
                        report = json.loads(result.stdout)[0]
                        self.assertEqual(report['messages'], [], report)
                        source.write_text(('const unused = require("react");\n' if extension == 'cjs' else 'import unused from "react";\n') + source.read_text())
                        result = lint()
                        self.assertEqual(result.returncode, 0 if extension == 'cjs' else 1, result.stderr + result.stdout)
                        rules = [m['ruleId'] for m in json.loads(result.stdout)[0]['messages']]
                        self.assertIn('unused-imports/no-unused-vars' if extension == 'cjs' else 'unused-imports/no-unused-imports', rules)

    def test_hook_with_real_eslint(self):
        self.check_hook(legacy=False)

    def test_hook_with_legacy_eslint(self):
        self.check_hook(legacy=True)

    def test_codex_hook_with_real_eslint(self):
        self.check_hook(legacy=False, codex=True)

    def test_codex_hook_with_legacy_eslint(self):
        self.check_hook(legacy=True, codex=True)

    def check_hook(self, legacy, codex=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            package = root / 'frontend'
            package.mkdir()
            (package / 'node_modules').symlink_to(Path(MODULES).resolve(), target_is_directory=True)
            if legacy:
                (package / '.eslintrc.cjs').write_text('module.exports = {root:true,parserOptions:{ecmaVersion:2020,sourceType:"module"},rules:{"no-unused-vars":"error"}};')
            else:
                (package / 'eslint.config.mjs').write_text('export default [{rules:{"no-unused-vars":"error"}}];')
            (root / '.gitignore').write_text('node_modules/\n')
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            source = package / '한글 파일.js'
            source.write_text('const unused = 1;\n')
            def hook(payload):
                data = json.loads(payload)
                data['cwd'] = str(root)
                return subprocess.run(['/bin/bash', str(ROOT / 'assets/frontend-lint-stop.sh'),
                                       '--codex' if codex else '--claude'],
                                      cwd=root, input=json.dumps(data), capture_output=True, text=True,
                                      env=dict(os.environ, CLAUDE_PROJECT_DIR=str(root),
                                               ESLINT_USE_FLAT_CONFIG="false" if legacy else "true"))
            failed = hook('{}')
            self.assertEqual(failed.returncode, 2, failed.stderr)
            self.assertIn('no-unused-vars', failed.stderr)
            self.assertEqual(hook('{"stop_hook_active": true}').returncode, 0)
            source.write_text('export const used = 1;\n')
            passed = hook('{}')
            self.assertEqual(passed.returncode, 0, passed.stderr)
            if codex:
                self.assertEqual(json.loads(passed.stdout), {})


if __name__ == '__main__':
    unittest.main()
