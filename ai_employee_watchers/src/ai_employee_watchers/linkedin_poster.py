# linkedin_poster.py - Automatically post on LinkedIn for business/sales
import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInPoster')

# Dry run mode
import os
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'


class LinkedInPoster:
    """
    Posts content to LinkedIn for business/sales purposes.
    Reads draft posts from /Approved/LINKEDIN_POST_*.md files.
    """

    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.drafts = self.vault_path / 'Drafts'

        # Ensure directories exist
        for folder in [self.approved, self.done, self.logs, self.drafts]:
            folder.mkdir(parents=True, exist_ok=True)

        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)

    def _log_action(self, action: str, target: str, result: str, details: str = ""):
        """Log action to audit log"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        entries = []
        if log_file.exists():
            try:
                with open(log_file) as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        entries.append({
            'timestamp': datetime.now().isoformat(),
            'action_type': action,
            'actor': 'linkedin_poster',
            'target': target,
            'result': result,
            'details': details,
            'dry_run': DRY_RUN
        })

        with open(log_file, 'w') as f:
            json.dump(entries, f, indent=2)

    def _parse_post_file(self, file_path: Path) -> dict:
        """Parse a LinkedIn post file"""
        content = file_path.read_text()
        post_data = {
            'content': '',
            'hashtags': [],
            'image': None
        }

        # Parse frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                fm_text = parts[1].strip()
                body = parts[2].strip()

                for line in fm_text.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        if key.strip() == 'hashtags':
                            post_data['hashtags'] = [h.strip() for h in value.split(',')]
                        elif key.strip() == 'image':
                            post_data['image'] = value.strip()

                # Extract post content (everything after ## Post Content)
                if '## Post Content' in body:
                    post_content = body.split('## Post Content', 1)[1]
                    # Remove any subsequent sections
                    if '##' in post_content:
                        post_content = post_content.split('##')[0]
                    post_data['content'] = post_content.strip()
                else:
                    post_data['content'] = body

        return post_data

    def post_to_linkedin(self, page, post_content: str, hashtags: list = None) -> bool:
        """Post content to LinkedIn"""
        try:
            # Navigate to LinkedIn feed
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            page.wait_for_load_state('networkidle', timeout=15000)

            # Click "Start a post" button
            start_post = page.query_selector('button[class*="share-box-feed-entry__trigger"]') or \
                         page.query_selector('[data-testid="share-box"]') or \
                         page.query_selector('button:has-text("Start a post")')

            if not start_post:
                logger.error('Could not find "Start a post" button')
                return False

            start_post.click()
            time.sleep(2)

            # Find the post editor
            editor = page.query_selector('[role="textbox"][contenteditable="true"]') or \
                     page.query_selector('[data-testid="share-to-feed-text-area"]') or \
                     page.query_selector('.ql-editor')

            if not editor:
                logger.error('Could not find post editor')
                return False

            # Build full post with hashtags
            full_content = post_content
            if hashtags:
                full_content += '\n\n' + ' '.join(f'#{tag}' for tag in hashtags)

            # Type the post
            editor.click()
            editor.fill(full_content)
            time.sleep(1)

            if DRY_RUN:
                logger.info('[DRY RUN] Post content prepared but not submitted')
                logger.info(f'[DRY RUN] Content preview: {full_content[:100]}...')
                # Close the modal without posting
                close_btn = page.query_selector('[aria-label="Dismiss"]') or \
                            page.query_selector('button:has-text("Discard")')
                if close_btn:
                    close_btn.click()
                return True

            # Click Post button
            post_btn = page.query_selector('button:has-text("Post")') or \
                       page.query_selector('[data-testid="share-actions-post-button"]')

            if post_btn:
                post_btn.click()
                time.sleep(3)
                logger.info('Post submitted successfully!')
                return True
            else:
                logger.error('Could not find Post button')
                return False

        except Exception as e:
            logger.error(f'Error posting to LinkedIn: {e}')
            return False

    def process_approved_posts(self, page) -> int:
        """Process all approved LinkedIn post files"""
        post_files = list(self.approved.glob('LINKEDIN_POST_*.md'))

        if not post_files:
            logger.debug('No approved LinkedIn posts to process')
            return 0

        processed = 0
        for post_file in post_files:
            logger.info(f'Processing: {post_file.name}')

            try:
                post_data = self._parse_post_file(post_file)

                if not post_data['content']:
                    logger.warning(f'No content found in {post_file.name}')
                    continue

                success = self.post_to_linkedin(
                    page,
                    post_data['content'],
                    post_data['hashtags']
                )

                if success:
                    # Move to Done
                    done_path = self.done / post_file.name
                    post_file.rename(done_path)

                    self._log_action(
                        'linkedin_post',
                        post_file.name,
                        'success',
                        f'Posted to LinkedIn: {post_data["content"][:50]}...'
                    )
                    processed += 1
                else:
                    self._log_action(
                        'linkedin_post',
                        post_file.name,
                        'failed',
                        'Could not post to LinkedIn'
                    )

            except Exception as e:
                logger.error(f'Error processing {post_file.name}: {e}')
                self._log_action('linkedin_post', post_file.name, 'error', str(e))

        return processed

    def create_draft_post(self, content: str, hashtags: list = None, topic: str = "business"):
        """Create a draft post file for approval"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}_{topic}.md"
        filepath = self.drafts / filename

        hashtags_str = ', '.join(hashtags) if hashtags else 'business, sales'

        draft_content = f'''---
type: linkedin_post
topic: {topic}
hashtags: {hashtags_str}
created: {datetime.now().isoformat()}
status: draft
---

# LinkedIn Post Draft

## Post Content
{content}

## Hashtags
{' '.join(f'#{tag}' for tag in (hashtags or ['business', 'sales']))}

## To Approve
Move this file to `/Approved/` to post on LinkedIn.

---
*Generated by AI Employee*
'''
        filepath.write_text(draft_content)
        logger.info(f'Created draft post: {filename}')
        return filepath

    def run(self, headless: bool = False):
        """Main run loop"""
        mode = "DRY RUN" if DRY_RUN else "LIVE"
        logger.info(f'Starting LinkedIn Poster [{mode} MODE]')
        logger.info(f'Vault path: {self.vault_path}')
        logger.info(f'Session path: {self.session_path}')

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=headless,
                args=['--disable-blink-features=AutomationControlled'],
                viewport={'width': 1280, 'height': 800}
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to LinkedIn
            logger.info('Navigating to LinkedIn...')
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            time.sleep(3)

            # Check if logged in
            if 'login' in page.url.lower() or 'signin' in page.url.lower():
                logger.info('Please log in to LinkedIn in the browser window...')
                page.wait_for_url('**/feed/**', timeout=120000)
                logger.info('Login successful!')

            # Process approved posts
            processed = self.process_approved_posts(page)
            logger.info(f'Processed {processed} post(s)')

            browser.close()

        logger.info('LinkedIn Poster finished.')


def main():
    """Main entry point"""
    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    default_session = Path(__file__).parent.parent.parent.parent / 'credentials' / 'linkedin_session'

    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    vault_path = Path(args[0]) if len(args) > 0 else default_vault
    session_path = Path(args[1]) if len(args) > 1 else default_session

    if not vault_path.exists():
        logger.error(f'Vault path not found: {vault_path}')
        sys.exit(1)

    headless = '--headless' in sys.argv
    test_mode = '--test' in sys.argv
    create_draft = '--create-draft' in sys.argv

    poster = LinkedInPoster(str(vault_path), str(session_path))

    if test_mode:
        logger.info('Running in TEST MODE')
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto('https://www.linkedin.com', timeout=30000)
            title = page.title()
            logger.info(f'Successfully loaded LinkedIn: {title}')
            browser.close()
        logger.info('TEST PASSED - LinkedIn is accessible')
    elif create_draft:
        # Create a sample draft post
        sample_content = """Excited to share that our AI-powered solutions are helping businesses automate their workflows and save valuable time!

Whether you're looking to streamline operations, improve customer response times, or gain insights from your data - we've got you covered.

Let's connect and discuss how we can help your business grow!"""
        poster.create_draft_post(
            sample_content,
            hashtags=['AI', 'Automation', 'Business', 'Productivity'],
            topic='ai_services'
        )
    else:
        poster.run(headless=headless)


if __name__ == '__main__':
    main()
