---
description: Rebuild and deploy the British Cinema static site (titan.tail1a2109.ts.net/british-cinema/)
allowed-tools: Bash
---

Trigger the British Cinema rebuild + redeploy on titan, then show the post-deploy status.

```bash
ssh titan 'cd /home/stu/projects/british-cinema && ./deploy.sh && echo --- status --- && ./status.sh'
```

If the deploy fails, surface the relevant error lines (likely build failure in `/home/stu/projects/kometa/posters/build_site.py` or rsync permission issue). Don't dump the full output unless asked.
