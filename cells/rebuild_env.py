import os, subprocess, re

# load /root/.env
new = {}
out = subprocess.run(['bash','-c','set -a; source /root/.env; env'], capture_output=True, text=True).stdout
for line in out.splitlines():
    if '=' in line:
        k,_,v = line.partition('=')
        new[k]=v

# load old cell env
old = {}
for line in open('/root/.openclaw/workspace/cells/claude/.cell-env.sh'):
    line=line.strip()
    if line.startswith('export ') and '=' in line:
        k,v = line[7:].split('=',1); old[k]=v.strip().strip('"').strip("'")

# canonical set: old order, new values, carry vars only in old (BASE urls etc.)
keys = list(old.keys())
for k in new:
    if k not in keys and re.fullmatch(r'[A-Z0-9_]+', k) and k not in ('PWD','SHLVL','_'):
        keys.append(k)
lines = ['# cells/.cell-env.sh — CANONICAL (symlinked by all cells; 2026-09-27 rotation)',
         '# source of truth: /root/.env (Casey). Regenerate: python3 cells/rebuild_env.py']
for k in keys:
    v = new.get(k, old.get(k, ''))
    if not v: continue
    if re.search(r'[\s$`"\'\\]', v):
        v = "'" + v.replace("'", "'\\''") + "'"
    lines.append(f'export {k}={v}')
content = '\n'.join(lines) + '\n'

p = '/root/.openclaw/workspace/cells/.cell-env.sh'
with open(p, 'w') as f:
    f.write(content)
os.chmod(p, 0o600)
print('canonical written:', len(keys), 'vars')

# symlink the five cell copies
import glob
for cell in glob.glob('/root/.openclaw/workspace/cells/*/.cell-env.sh'):
    if os.path.islink(cell) or not os.path.samefile(cell, p) if os.path.exists(cell) else True:
        pass
    os.remove(cell)
    os.symlink(p, cell)
    print('linked:', cell)
print('done')
