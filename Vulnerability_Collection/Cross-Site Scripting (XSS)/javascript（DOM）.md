DOM (Document Object Model) 操作是指通过 JavaScript 来访问和操作 HTML 文档的结构、样式和内容。DOM 将 HTML 文档表示为节点树，允许开发者动态地修改页面。

文档是根节点（`document`），包含元素（如`<div>`）、属性（如`class`）、文本节点等。
对应的DOM树：

```
document
└── html
    └── body
        └── div#content
             └── "Hello" (文本节点)
```
## 基本 DOM 操作

### 获取元素
```javascript
// 通过ID获取
const element = document.getElementById('id');

// 通过类名获取（返回HTMLCollection）
const elements = document.getElementsByClassName('class');

// 通过标签名获取（返回HTMLCollection）
const tags = document.getElementsByTagName('div');

// 通过CSS选择器获取（返回第一个匹配元素）
const firstMatch = document.querySelector('.class');

// 通过CSS选择器获取所有匹配元素（返回NodeList）
const allMatches = document.querySelectorAll('div.class');

```
### 修改内容
```javascript
// 修改文本内容
element.textContent = '新文本';

// 修改HTML内容
element.innerHTML = '<strong>加粗文本</strong>';

// 修改属性
element.setAttribute('data-id', '123');
const value = element.getAttribute('data-id');
element.removeAttribute('data-id');

// 修改样式
element.style.color = 'red';
element.style.backgroundColor = '#fff';
```
### 创建和添加元素
```javascript
// 创建新元素
const newElement = document.createElement('div');

// 添加子元素
parentElement.appendChild(newElement);

// 在特定位置插入元素
parentElement.insertBefore(newElement, referenceElement);

// 克隆元素
const clonedElement = element.cloneNode(true); // true表示深度克隆
```
### 删除元素
```javascript
// 移除子元素
parentElement.removeChild(childElement);

// 现代方法（不需要知道父元素）
element.remove();
```
## 事件处理
```javascript
// 添加事件监听器
element.addEventListener('click', function(event) {
  console.log('元素被点击了', event.target);
});

// 移除事件监听器
function handleClick() { /* ... */ }
element.addEventListener('click', handleClick);
element.removeEventListener('click', handleClick);
```
## 高级 DOM 操作

### 遍历 DOM
```javascript
// 获取父元素
const parent = element.parentNode;

// 获取子元素
const firstChild = element.firstChild;
const children = element.childNodes; // NodeList
const childrenElements = element.children; // HTMLCollection

// 获取兄弟元素
const nextSibling = element.nextSibling;
const previousSibling = element.previousSibling;
```
### 类名操作
```javascript
// 添加类
element.classList.add('new-class');

// 移除类
element.classList.remove('old-class');

// 切换类
element.classList.toggle('active');

// 检查类是否存在
if (element.classList.contains('some-class')) {
  // ...
}
```
