# chrisdoescloud.com

Personal site — static HTML generated from Markdown, hosted on S3 + CloudFront.

## Prerequisites

- [uv](https://github.com/astral-sh/uv)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
- AWS credentials with access to the `chrisdoescloud-site` stack

## Local development

```bash
make serve   # build + serve at http://localhost:8080
```

## Deploy

```bash
make deploy  # build, sync to S3, invalidate CloudFront
```

To provision or update infrastructure:

```bash
make infra   # sam deploy (CloudFormation stack)
```

## Adding a post

Create `posts/<slug>.md` with YAML frontmatter:

```markdown
---
title: My Post Title
date: 2026-01-01
draft: false
---

Post content here.
```

Set `draft: true` to exclude from the build.

## Project layout

```
posts/          Markdown blog posts
about/          About page
cv/             CV page (disabled by default)
src/styles/     CSS
static/         Assets copied verbatim to dist/
build.py        Static site generator
template.yaml   AWS SAM / CloudFormation template
Makefile        Common tasks
```
