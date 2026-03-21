# Security

## Supported versions

Security fixes are applied to the **default branch** (`main`) as needed. Deployed instances should track that branch or tagged releases derived from it. This is a small application without a formal LTS matrix; use the latest commit you have tested.

## Reporting a vulnerability

**Please do not** open a public GitHub issue for undisclosed security problems.

1. **Preferred**: Use [GitHub private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability) for this repository if it is enabled ( **Security** tab → **Report a vulnerability** ).

2. **Otherwise**: Contact the repository maintainers through a private channel they publish on the GitHub org or user profile (for example, verified email or organization security contact), and include:
   - A short description of the issue and its impact
   - Steps to reproduce (or proof-of-concept), if safe to share
   - Affected component (e.g. Flask app, dependency, deployment surface)

You should receive an acknowledgment within a few business days for valid reports. We will coordinate disclosure once a fix is available.

## Scope

In scope for security reports:

- This application’s code (`app.py`, templates, static assets) and how it is run in production (e.g. Gunicorn, `PORT` binding)
- Handling of untrusted input that reaches the server
- Dependency vulnerabilities that materially affect this project when used as documented

Generally **out of scope**: denial-of-service via large Statcast date ranges (operational/load concern), issues in third-party services (MLB, `pybaseball`, CDNs) unless this repo can mitigate them safely.

## Secure deployment reminders

Operators should:

- Run behind a managed host or reverse proxy with TLS in production
- Keep Python dependencies updated (`pip install -r requirements.txt` from a locked or reviewed set)
- Not enable Flask debug mode or expose debug endpoints in production
