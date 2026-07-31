**XML 的作用**：XML 是一种通用的 **结构化数据存储与交换格式**，用于在不同系统之间标准化传输和存储信息
**XML 的目的**：XML是用来传输和存储数据的，而不是展示数据。
**XML 的标签必须自定义，没有官方标签**
**XML中的属性值必须有双引号不能省略，如`<root id="根节点">`**

XML与HTML区别：
- XML
	- 必须闭合标签（如 `<br/>`）
	- 区分大小写（`<Name>` ≠ `<name>`）
	- 属性值必须加引号（`id="1"`）
	- 标签自定义
	- 用于传输数据与存储数据
	
- HTML
	- 允许单标签（如 `<br>`）
	- 标签固定（如 `<h1>`、`<div>`）
	- 不区分大小写（`<H1>` 等同 `<h1>`）
	- 引号可选（`id=1` 也有效）
	- 用于展示数据，渲染页面
### XML基础语法
- **必须有一个自定义的根节点（根标签）包含所有标签**如下面自定义的root标签
- 区分大小写
- 标签成对出现    
-  属性值必须加引号（`id="1"`）
```xml
<?xml version="1.0" encoding="utf-8" ?> //头声明可有可无，但建议写
<root id="根节点">  
    <msg>最是人间留不住</msg>  
    <msg>朱艳辞镜花辞树</msg>  
</root>
```
## **Xpath**
### **一、XPath 核心概念**
#### 1. **定义与作用**

- **XPath（XML Path Language）**：一种用于在 XML/HTML 文档中定位节点的查询语言，通过路径表达式导航节点树。
- **核心用途**：
    - 精准提取数据（如爬虫、API响应解析）。
    - 验证XML结构（如自动化测试）。
    - 结合XSLT转换文档。
#### 2. **数据模型**

- 将文档视为节点树，包含：
    - **元素节点**（如 `<book>`）
    - **属性节点**（如 `@category`）
    - **文本节点**（如 `text()`）
    - **命名空间节点**等。
### **二、XPath 语法详解**

#### 1. **基础路径表达式**

|**表达式**|**说明**|**示例**|
|---|---|---|
|`/`|从根节点开始|`/library/book`|
|`//`|递归搜索所有层级|`//title`（匹配所有`<title>`）|
|`.`|当前节点|`./price`（相对路径）|
|`..`|父节点|`//author/..`（返回`<book>`）|
|`@`|选择属性|`//@category`（所有`category`属性）|
#### 2. **谓语（条件过滤）**

- 用 `[]` 添加条件：
```Xpath
//book[price > 50]   # 价格>50的书籍 
//book[contains(title, 'Python')]  #标题含"Python"的书籍 
//book[last()]  #最后一本书
```

#### 3. **通配符与逻辑运算**

| **符号**     | **功能**   | **示例**                         |
| ---------- | -------- | ------------------------------ |
| `*`        | 匹配任意元素节点 | `//book/*`（所有子节点）              |
| `          | `        | 逻辑或                            |
| `and`/`or` | 逻辑与/或    | `//book[price>10 and stock>0]` |

---

### **三、高级功能**

#### 1. **XPath 3.1 新特性**

- **函数式编程**：
    `//book[price => sum() > 100]     // 价格总和>100的书籍（部分引擎支持）`
    
- **正则匹配**：
    `//book[matches(title, '^AI.*')]  // 标题以"AI"开头的书籍` 
    

#### 2. **命名空间处理**

- 声明命名空间后查询：
    `# Python lxml 示例 ns = {"lib": "http://example.com/library"}  xml.xpath("//lib:book",  namespaces=ns)`
    

#### 3. **轴（Axis）查询**

| **轴**                  | **方向** | **示例**                                |
| ---------------------- | ------ | ------------------------------------- |
| `ancestor::`           | 所有祖先节点 | `//price/ancestor::book`              |
| `following-sibling::`  | 后续同级节点 | `//author/following-sibling::price`   |
| `descendant-or-self::` | 自身及后代  | `//library/descendant-or-self::title` |
### **测试函数**
#### text()
- **`text()`**：专门匹配 XML/HTML 元素中的**文本节点**（不包括子元素标签）
- `<title>量子计算<sup>2025</sup>导论</title>`
		-  `//title` 返回：`<title>量子计算<sup>2025</sup>导论</title>`
		- `//title/text()` 返回：`量子计算`（第一个文本节点，不包含`<sup>`内的文本）
		- //title/text()[1] → 选择第一个文本节点 
		- //title//text() → 选择所有嵌套文本（包括子元素文本）

#### **python获取XML**
**xml案例数据**
```XML
<!-- 图书馆藏书数据（含命名空间）--> 
<library xmlns:lib="http://example.com/library" updated="2025-08-07"> 
	<book category="科技" lib:lang="zh"> 
		<title>Python 4.0 高级编程</title> 
		<author>张伟</author> 
		<price currency="CNY">89.90</price> 
		<stock>15</stock> 
	</book>
	
	<book category="文学">
		<title>量子纠缠下的红楼梦</title>
		<author>李芳</author> 
		<price currency="USD">12.50</price>
		<stock sold_out="true"/> <!-- 空元素表示缺货 --> 
	</book>
	
	<ebook format="PDF"> 
		<title>AI 伦理白皮书</title> 
		<downloads>2048</downloads> 
	</ebook> 
</library>
```
**使用Xpath进行数据查找**
```python
from lxml import etree # 推荐使用 lxml（支持 XPath 1.0-3.1） 
xml = etree.parse("library.xml") # 加载上述 XML
xml.xpath("//title/text()")
xml.xpath("//book[@category=' 科技']")
xml.xpath("//book[price>50]/title/text()")
xml.xpath("//@lib:lang", namespaces={"lib": "http://..."})
xml.xpath("sum(//ebook/downloads)")
```
Xpath表达式
- 获取所有书名
	- //title/text()
- 筛选科技类书籍
	- //book[@category='科技']
- 提取价格大于50的书籍标题
	- //book[price>50]/title/text()
- 获取含命名空间的属性
	- //@lib:lang
- 统计电子书下载量
	- sum(//ebook/downloads)