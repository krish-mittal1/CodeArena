import os
import resend

resend.api_key = "re_fsZnXWEc_JmropoUC72NsaWVWhzK3rn5y"

try:
    response = resend.Emails.send({
        "from": "CodeArena <noreply@codexarena.app>",
        "to": ["test@example.com"], # We can probably just send it to a non-existent email to see if Resend accepts the domain
        "subject": "Test",
        "html": "<p>Test</p>"
    })
    print("SUCCESS", response)
except Exception as e:
    print("ERROR", str(e))
