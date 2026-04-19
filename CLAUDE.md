# chrisdoescloud.com

Personal static site deployed to AWS (S3 + CloudFront via SAM).

## How it works

- `build.py` — Python script that converts Markdown → HTML and writes to `dist/`
- `posts/*.md` — blog posts with YAML frontmatter
- `about/index.md` — about page
- `cv/` — CV page (toggled via `CV_PUBLISHED` flag in `build.py`)
- `src/styles/main.css` — site stylesheet
- `static/` — assets copied verbatim to `dist/`
- `template.yaml` — AWS SAM template (S3 bucket + CloudFront distribution)
- `samconfig.toml` — SAM deploy config
- `.github/workflows/` — CI/CD via GitHub Actions with OIDC auth

## Common tasks

```bash
make build      # run build.py, output goes to dist/
make deploy     # sam build + sam deploy
```

## Adding a post

Create `posts/<slug>.md` with frontmatter:

```markdown
---
title: My Post
date: 2026-01-01
draft: false
---
```

## Stack

Python 3.x · AWS SAM · S3 · CloudFront · GitHub Actions
