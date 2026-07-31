# Attack Report -- dasctf-shrine-ssti

## Target Summary
- URL: https://65bde0e59a06b163d9baf709.http-ctf2.dasctf.com/
- Server: openresty (reverse proxy)
- Framework: Flask (Python 2.7.16 / Werkzeug 0.15.5)
- Vulnerability: Server-Side Template Injection (SSTI) in Jinja2

## Vulnerability Discovered
- Type: SSTI with parenthese filter and blacklist bypass
- Location: `/shrine/<path:shrine>` endpoint
- Filters applied:
  - `(` and `)` are stripped from input
  - `config` and `self` nullified via `{% set x=None%}`
- How it was found: Source code revealed `render_template_string` with user-controlled input

## Exploitation Chain
1. **Recon** -- curl revealed the full Flask source code at `/` with the `/shrine/` endpoint
2. **SSTI confirmation** -- `{{7*7}}` returned `49`
3. **Blacklist analysis** -- `config` and `self` set to None, parentheses stripped
4. **Workaround** -- Used `url_for.__globals__` to access Flask internals without calling functions or using blocked words
5. **Flag extraction** -- `{{url_for.__globals__['current_app'].__dict__['config']}}` revealed the full Flask config including the FLAG

## Flag Captured
| Flag                                         | Location             | Method                                               |
| -------------------------------------------- | -------------------- | ---------------------------------------------------- |
| `CTF2{52c7715a-13c3-4a6f-be1b-420f72e8bc81}` | `app.config['FLAG']` | SSTI via `url_for.__globals__['current_app'].config` |

## Lessons Learned
- `url_for` and `get_flashed_messages` are Flask functions whose `__globals__` expose `current_app`, `request`, `os`, and `__builtins__`
- Parentheses filter prevents function calls but not attribute/item access or Jinja2 filter syntax
- `{% for key in obj %}` blocks work without parentheses
- `config` variable nullification doesn't affect attribute access (`current_app.config`)
- Flask Config class inherits from dict, so `['FLAG']` bracket notation works

## Files Saved
- recon/index-source.html
- recon/headers.txt
- flags/flag.txt
- attack-report.md
