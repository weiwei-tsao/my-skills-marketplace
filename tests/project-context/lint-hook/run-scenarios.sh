#!/usr/bin/env bash
# Runs setup's lint-edited-file.sh template against real ESLint and Ruff.
# usage: run-scenarios.sh <work-dir>
# First run installs ESLint 9.17.0 (npm) and Ruff 0.8.4 (uv venv) into <work-dir>;
# later runs reuse them. Needs node/npm, uv and python3. No API calls.
# Prints PASS/FAIL per scenario: linter exit, hook exit, expected hook exit.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
TPL="$HERE/../../../plugins/project-context/skills/setup/templates/hooks/lint-edited-file.sh"
L=${1:?usage: run-scenarios.sh <work-dir>}
mkdir -p "$L/eslint-proj" "$L/ruff-proj"
L=$(cd "$L" && pwd)
FAILS=0
BASEPATH="/usr/bin:/bin:/usr/sbin:/sbin:$(dirname "$(command -v node)")"
if [ ! -x "$L/eslint-proj/node_modules/.bin/eslint" ]; then
  (cd "$L/eslint-proj" && npm init -y >/dev/null && npm i -D --no-audit --no-fund eslint@9.17.0 @eslint/js@9.17.0 >/dev/null) || exit 1
fi
if [ ! -x "$L/venv/bin/ruff" ]; then
  uv venv -q "$L/venv" && VIRTUAL_ENV="$L/venv" uv pip install -q ruff==0.8.4 || exit 1
fi

make_hook() { # dir cmd exts
  mkdir -p "$1/.claude/hooks"
  sed -e "s|__LINT_CMD__|$2|" -e "s|__LINT_EXTS__|$3|" "$TPL" > "$1/.claude/hooks/lint-edited-file.sh"
  chmod +x "$1/.claude/hooks/lint-edited-file.sh"
}

run() { # name dir file path-env expected-hook-exit
  local name=$1 dir=$2 file=$3 p=$4 want=${5:-?} t0 t1 rc lrc err
  cmd=$(sed -n 's/^LINT_CMD="\([^"]*\)".*/\1/p' "$dir/.claude/hooks/lint-edited-file.sh")
  lrc=$(cd "$dir" && PATH=$p $cmd "$file" >/dev/null 2>&1 </dev/null; echo $?)
  t0=$(python3 -c 'import time;print(time.time())')
  err=$(printf '{"tool_name":"Edit","tool_input":{"file_path":"%s"}}' "$file" \
        | CLAUDE_PROJECT_DIR="$dir" PATH=$p "$dir/.claude/hooks/lint-edited-file.sh" 2>&1 >/dev/null)
  rc=$?
  t1=$(python3 -c 'import time;print(time.time())')
  ok=$([ "$rc" = "$want" ] && echo PASS || echo FAIL)
  [ "$ok" = FAIL ] && FAILS=$((FAILS+1))
  printf '%-4s %-34s linter=%-3s hook=%-2s want=%-2s %5.1fs | %s\n' "$ok" "$name" "$lrc" "$rc" "$want" \
    "$(python3 -c "print($t1-$t0)")" "$(printf '%s' "$err" | grep -v '^\s*$' | sed -n '2,3p' | tr '\n' ' ' | cut -c1-150)"
}

### ESLint project
E=$L/eslint-proj
cat > $E/eslint.config.js <<'EOF'
import js from "@eslint/js";
export default [js.configs.recommended,
  { rules: { "no-console": "warn" } },
  { ignores: ["vendor/**"] }];
EOF
printf '{"type":"module"}' > /dev/null
node -e 'const p=require("'$E'/package.json");p.type="module";require("fs").writeFileSync("'$E'/package.json",JSON.stringify(p,null,2))'
mkdir -p $E/src $E/vendor "$E/src/with space"
echo 'export const a = 1;'                       > $E/src/clean.js
echo 'const unused = 1; export const b = 2;'     > $E/src/error.js
printf '/* global console */\nconsole.log("hi");\nexport const c = 3;\n' > $E/src/warn.js
echo 'const x = 1; export {}'                    > $E/vendor/ignored.js
echo 'const y = ; export {}'                     > $E/src/syntax.js
echo 'export const d = 4;'                       > "$E/src/with space/ok.js"
echo 'not code'                                  > $E/README.md
make_hook $E "node_modules/.bin/eslint" "js jsx ts tsx"
echo "== ESLint 9.17.0, LINT_CMD=node_modules/.bin/eslint"
run "E1 clean"                 $E src/clean.js  "$BASEPATH" 0
run "E2 lint error"            $E src/error.js  "$BASEPATH" 2
run "E3 warning only"          $E src/warn.js   "$BASEPATH" 0
run "E4 syntax error"          $E src/syntax.js "$BASEPATH" 2
run "E5 ignored by config"     $E vendor/ignored.js "$BASEPATH" 0
run "E6 path with space"       $E "src/with space/ok.js" "$BASEPATH" 0
run "E7 ext not linted (.md)"  $E README.md     "$BASEPATH" 0
run "E8 absolute path"         $E "$E/src/error.js" "$BASEPATH" 2
cp $E/eslint.config.js $E/eslint.config.js.bak
echo 'export default [ {{ broken' > $E/eslint.config.js
run "E9 broken config"         $E src/clean.js  "$BASEPATH" 1
rm $E/eslint.config.js
run "E10 no config file"       $E src/clean.js  "$BASEPATH" 1
mv $E/eslint.config.js.bak $E/eslint.config.js
mv $E/node_modules $E/node_modules.off
run "E11 eslint not installed"  $E src/clean.js  "$BASEPATH" 1
mv $E/node_modules.off $E/node_modules
make_hook $E "eslint" "js"
run "E12 bare eslint, not on PATH" $E src/clean.js "$BASEPATH" 1

### Ruff project
R=$L/ruff-proj
cat > $R/pyproject.toml <<'EOF'
[project]
name = "t"
version = "0"
[tool.ruff]
extend-exclude = ["vendor"]
EOF
mkdir -p $R/src $R/vendor
echo 'X = 1'                       > $R/src/clean.py
printf 'import os\nX = 1\n'        > $R/src/error.py
printf 'def f(:\n    pass\n'       > $R/src/syntax.py
printf 'import os\n'               > $R/vendor/excluded.py
make_hook $R "ruff check --force-exclude" "py"
RP="$L/venv/bin:$BASEPATH"
echo "== Ruff 0.8.4, LINT_CMD=ruff check --force-exclude"
run "R1 clean"                 $R src/clean.py  "$RP" 0
run "R2 lint error"            $R src/error.py  "$RP" 2
run "R3 syntax error"          $R src/syntax.py "$RP" 2
run "R4 excluded, passed explicitly" $R vendor/excluded.py "$RP" 0
cp $R/pyproject.toml $R/pyproject.toml.bak
printf '[tool.ruff]\nline-length = "long"\n' >> $R/pyproject.toml
run "R5 invalid config"        $R src/clean.py  "$RP" 1
mv $R/pyproject.toml.bak $R/pyproject.toml
run "R6 ruff not installed"    $R src/clean.py  "$BASEPATH" 1

echo "failed: $FAILS"
[ "$FAILS" -eq 0 ]
