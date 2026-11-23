#!/usr/bin/env python
"""Pre-commit security hook: guarantees only verified team members can author commits."""
import os
import subprocess
import sys

ALLOWED_EMAILS = {
    "abdullah262686@gmail.com",
    "abdullahmudasir27@gmail.com",
    "talhabhattiak47@gmail.com",
    "danialhameed755@gmail.com",
    "ahmadzahid5029@gmail.com"
}

BLOCKED_PATTERNS = ["hasna", "rameesha", "bsdsf23a005", "bsdsf23a023"]

def main():
    # Check author email
    author_email = os.environ.get("GIT_AUTHOR_EMAIL")
    if not author_email:
        p = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True)
        author_email = p.stdout.strip()
    
    if author_email.lower() not in ALLOWED_EMAILS:
        print(f"❌ [BLOCKED] Unauthorized commit author email: {author_email}")
        print(f"Allowed team emails are only:\n - " + "\n - ".join(sorted(ALLOWED_EMAILS)))
        sys.exit(1)
        
    print(f"✓ Author verified: {author_email}")
    sys.exit(0)

if __name__ == "__main__":
    main()
