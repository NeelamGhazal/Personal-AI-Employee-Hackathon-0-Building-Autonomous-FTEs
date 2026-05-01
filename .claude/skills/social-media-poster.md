# Skill: Social Media Poster

## Description
Post content to Facebook, Instagram, and Twitter using Playwright browser automation. Supports session persistence for staying logged in.

## Supported Platforms

### Facebook
```bash
uv run python src/ai_employee_watchers/facebook_poster.py --test
uv run python src/ai_employee_watchers/facebook_poster.py "Your post content"
```

### Instagram
```bash
uv run python src/ai_employee_watchers/instagram_poster.py --test
uv run python src/ai_employee_watchers/instagram_poster.py "Your caption"
```

### Twitter/X
```bash
uv run python src/ai_employee_watchers/twitter_poster.py --test
uv run python src/ai_employee_watchers/twitter_poster.py "Your tweet (280 chars max)"
```

## Features
- **Session Persistence**: Stays logged in between runs
- **Screenshot Proof**: Captures screenshot after posting
- **Action Files**: Creates record in `/Business/Social_Media/`
- **Character Validation**: Twitter enforces 280 char limit

## Session Storage
Sessions stored in `/credentials/` (gitignored):
- `facebook_session/`
- `instagram_session/`
- `twitter_session/`

## First-Time Login
On first run, browser opens for manual login:
1. Run with `--test` flag
2. Complete login in browser window
3. Session saved for future runs

## MCP Server Integration
Use via `social_media_mcp_server.cjs`:
```json
{
  "tool": "social_post_twitter",
  "arguments": {
    "content": "Hello from AI Employee!"
  }
}
```

## Output Files
Each post creates action file:
```markdown
# Social Media Post: twitter
Posted: 2026-04-28T10:30:00
Platform: twitter
Content: Hello world!
Screenshot: /Business/Social_Media/screenshots/twitter_*.png
```

---
*AI Employee Gold Tier Skill*
