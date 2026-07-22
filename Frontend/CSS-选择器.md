# CSS 选择器

## 三种基础选择器

CSS 通过**选择器**（selector）指定样式应用到哪些 HTML 元素上。三种最基础的选择器：

| 选择器 | 语法 | 含义 | HTML 写法 | 特点 |
|--------|------|------|-----------|------|
| **元素选择器** | 直接写标签名，如 `div` `iframe` `p` | 选中该类型的所有标签 | 无需额外属性 | 范围最广，一整类标签全选中 |
| **class 选择器** | `.` + 类名，如 `.firstClick` `.red` | 选中所有 `class="类名"` 的元素 | `<div class="firstClick">` | **可复用**，多个元素可以共享同一个 class；一个元素也可以有多个 class（空格分隔） |
| **id 选择器** | `#` + id 名，如 `#step1` `#submit-btn` | 选中 `id="id名"` 的那个元素 | `<div id="step1">` | **页面中唯一**，一个 id 只能出现在一个元素上 |

## 示例

```html
<!-- HTML -->
<p id="title">这是标题</p>           <!-- id="title"，页面唯一 -->
<div class="red bold">红色加粗</div>  <!-- 两个 class：red 和 bold -->
<div class="red">只是红色</div>
<span class="red">也是红色</span>     <!-- class 可复用，span 也能用 -->
```

```css
/* 三个元素全变红，因为都有 class="red" */
.red { color: red; }

/* 只有 id="title" 的那个 p 字号变大 */
#title { font-size: 24px; }

/* 所有 div 加边框（上面两个 div 都会受影响） */
div { border: 1px solid black; }
```

## `.firstClick` 在 Clickjacking payload 中的含义

回顾多步骤 Clickjacking 中的这段 CSS：

```css
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
```

- `.firstClick, .secondClick` — 逗号表示"和"，即**所有 class 为 firstClick 或 secondClick 的元素**共享 `position/z-index` 等公共样式
- `.secondClick` — 单独覆盖 `top`/`left`，因为第二步按钮在页面中的位置与第一步不同

对应的 HTML：

```html
<div class="firstClick">Click me first</div>   <!-- 匹配 .firstClick -->
<div class="secondClick">Click me next</div>   <!-- 匹配 .secondClick -->
```

## 优先级（特异性）与层叠覆盖

当多个规则作用于同一个元素时，CSS 通过两层规则决定最终值。

### 第一层：优先级（特异性）

| 优先级 | 选择器 | 特异性值 |
|--------|--------|----------|
| 最高 | `#id` | (1, 0, 0) |
| 中等 | `.class` | (0, 1, 0) |
| 最低 | 元素标签 `div` | (0, 0, 1) |

### 第二层：书写顺序（层叠）

**优先级相同时，写在后面的覆盖前面的。** 而且只覆盖**重复的属性**，不重复的属性保留原值。

这就是 Clickjacking payload 中覆盖的工作原理：

```css
/* 第一段：两个诱饵的公共样式 */
.firstClick, .secondClick {       /* 特异性：(0, 1, 0) */
    position: absolute;            /* 两个都生效 */
    top: 330px;                    /* 初始值，.secondClick 会被覆盖 */
    left: 50px;                    /* 初始值，.secondClick 会被覆盖 */
    z-index: 1;                    /* 两个都生效 */
}

/* 第二段：单独调整第二个诱饵的位置 */
.secondClick {                     /* 特异性：(0, 1, 0) — 相同！ */
    top: 285px;                    /* 覆盖上面的 330px */
    left: 225px;                   /* 覆盖上面的 50px */
    /* position 和 z-index 没写 — 保留第一段的值，不变 */
}
```

`.secondClick` 的最终样式：

| 属性 | 最终值 | 来源 |
|------|--------|------|
| `position` | `absolute` | 第一段（未被覆盖） |
| `z-index` | `1` | 第一段（未被覆盖） |
| `top` | `285px` | 第二段（覆盖了第一段的 `330px`） |
| `left` | `225px` | 第二段（覆盖了第一段的 `50px`） |

**关键规则**：优先级相同 → 后写的赢 → **只赢在冲突的属性上**，不冲突的属性各自保留。

> 修正：`.firstClick, .secondClick` 和 `.secondClick` 的优先级完全相等（都是一个 class 选择器，特异性 `(0, 1, 0)`）。覆盖靠的是**书写顺序**，不是特异性差异。上一版说"更具体"是错误的。

## 复合写法

| 写法 | 含义 | 示例 |
|------|------|------|
| `A, B` | A **和** B（并集） | `div, p` → 所有 div 和所有 p |
| `A B` | A **里面的** B（后代） | `div p` → 所有在 div 内部的 p |
| `A.B` | 同时满足 A 和 B（且） | `div.red` → 所有 class 含 red 的 div |
| `A > B` | A 的**直接子元素** B | `div > p` → div 下一层的 p，不包含更深层 |
