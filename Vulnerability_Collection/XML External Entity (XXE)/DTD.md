**DTD** 的全称是 **Document Type Definition**。
- **作用**：它是一套用于定义XML文档结构和合法元素的语法规则。可以把它看作是XML文档的“蓝图”或“ schema”。
- **位置**：它可以内嵌在XML文档内部（内部DTD），也可以作为一个外部文件被引用（外部DTD）。
- **关键功能**：DTD允许我们声明“实体”。实体可以理解为变量或宏，在XML中用于定义引用普通文本或特殊字符的快捷方式。
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- 1. !DOCTYPE： 声明此XML文档遵循名为 "note" 的DTD规则 -->
<!DOCTYPE note [
    <!-- 2. !ELEMENT： 定义文档中每个元素的结构 -->

    <!-- 定义根元素 "note" 必须按顺序包含 to, from, heading, body 这四个子元素 -->
    <!ELEMENT note (to, from, heading, body)>

    <!-- 定义 "to", "from", "heading", "body" 元素的内容是纯文本字符串 (#PCDATA) -->
    <!ELEMENT to (#PCDATA)>
    <!ELEMENT from (#PCDATA)>
    <!ELEMENT heading (#PCDATA)>
    <!ELEMENT body (#PCDATA)>

    <!-- 3. !ENTITY： 定义实体（可重用的数据） -->

    <!-- 定义一个内部实体 "signature"，其内容是字符串 -->
    <!ENTITY signature "此致，敬礼！">

    <!-- 定义一个外部实体 "logo"，其内容来自一个外部图片文件 -->
    <!ENTITY logo SYSTEM "image/company_logo.png">

]>

<!-- XML文档正文，遵循上面DTD定义的规则 -->
<note>
    <to>张三</to>
    <from>李四</from>
    <heading>会议提醒</heading>
    <body>
        请于明天下午两点准时参加会议。
        <!-- 使用 &实体名; 的语法来引用实体 -->
        &signature;
    </body>
</note>
```
### 核心内容类型与组合符号

| 类型/符号           | 含义            | 示例                              |     |            |
| --------------- | ------------- | ------------------------------- | --- | ---------- |
| **`(#PCDATA)`** | **纯文本内容**     | `<!ELEMENT name (#PCDATA)>`     |     |            |
| **`EMPTY`**     | **空元素**       | `<!ELEMENT br EMPTY>`           |     |            |
| **`ANY`**       | **任何内容**（不推荐） | `<!ELEMENT container ANY>`      |     |            |
| **`(子元素...)`**  | **元素只能包含子元素** | `<!ELEMENT person (name, age)>` |     |            |
| **混合内容**        | **文本与子元素混合**  | `<!ELEMENT p (#PCDATA           | em  | strong)*>` |
