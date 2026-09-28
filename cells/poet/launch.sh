#!/bin/bash
set -a
source /root/.openclaw/workspace/cells/poet/.cell-env.sh
set +a
export HOME=/home/cell
export CLAUDE_CODE_TMPDIR=/home/cell/tmp
cd /root/.openclaw/workspace/cells/poet
exec setpriv --reuid=1000 --regid=1000 --clear-groups claude --permission-mode bypassPermissions
