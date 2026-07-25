# Attack Report -- dasctf-hackworld-blindsqli

## Target Summary
- URL: https://64413b275c657c39ad0bb422.http-ctf2.dasctf.com/index.php
- Server: openresty (nginx + lua)
- Backend: PHP/5.6.40
- Challenge hint: "All You Want Is In Table 'flag' and the column is 'flag'"

## Vulnerability Discovered
- Type: Blind Boolean-Based SQL Injection
- Location: POST parameter `id` on `index.php`
- How it was found: The page source revealed a form with `id` parameter and a hint about the `flag` table

## Exploitation Chain
1. **Target probing** -- curl revealed a simple form page with `id` POST parameter and explicit hint about `flag` table/column
2. **Response analysis** -- `id=1` returns "Hello, glzjin wants a girlfriend."; `id=2` returns "Do you want to be my girlfriend?" -- perfect boolean oracle
3. **Filter bypass identification** -- `select` followed by a space was filtered (anti-SQLi filter). The bypass was `select(...)from(...)` -- function-call style with no space after `select` keyword
4. **Binary search blind injection** -- used the boolean oracle to binary-search each character of `flag` from the `flag` table:
   - Payload: `if(ascii(substr((select(flag)from(flag)),N,1))>M,1,2)`
   - True condition: "Hello" in response
   - False condition: "girlfriend" in response
5. **Flag extraction** -- iterated positions 1-42, binary search per character (32-127 ASCII), stopped at `}`

## Flag Captured
| Flag | Location | Method |
|------|----------|--------|
| `CTF2{9a908905-5af8-4dc1-9a9b-0d9926a1c807}` | `flag` table, `flag` column | Blind boolean SQLi via binary search |

## Lessons Learned
- The filter blocked `select ` (select followed by space) but allowed `select(...)` with parentheses
- UUID-format flag (`flag{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}`) -- 36 hex chars + hyphens in UUID format inside `flag{}`
- The boolean oracle of "Hello" vs "girlfriend" response text made binary search efficient (log2(95) ~ 7 requests per character)

## Files Saved
- recon/index-source.html
- exploits/blind-sqli.py
- flags/flag.txt
- flags/blind-sqli-output.txt
- attack-report.md
