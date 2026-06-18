# Java

> 编译型 + 虚拟机运行，"一次编写到处运行"。企业级后端、Android 原生开发、大数据生态的核心语言。在安全领域，Java 反序列化（ysoserial）和 Spring 框架漏洞是两大重灾区。

---

## 一眼认出这是 Java

```java
// 一切都在类里——Java 是纯面向对象的
// 文件名必须与 public 类名相同：Hello.java

public class Hello {
    // 入口方法签名固定（记不住就复制粘贴）
    public static void main(String[] args) {
        // 变量必须声明类型
        String name = "Alice";
        int age = 25;
        boolean active = true;       // 小写 true/false
        double price = 19.99;

        // 可以用 var 推断类型（Java 10+）
        var items = new ArrayList<String>();

        System.out.println("Hello, " + name);   // 打印（不是 print）
    }
}
```

**一眼识别 Java 的关键特征：**
- 变量类型写在前面：`String name` 而不是 `name: String`
- `System.out.println()` 打印
- 到处都是 `public` / `private` / `class`
- 分号 `;` 结尾（和 C/C++/JavaScript 一样）

---

## 常用场景

| 场景      | 典型框架/工具                                |
| ------- | -------------------------------------- |
| 企业后端    | Spring Boot, Spring MVC, MyBatis       |
| Android | Android SDK, Kotlin（JVM 上的新语言）         |
| 大数据     | Hadoop, Spark, Flink, Kafka            |
| 中间件     | Tomcat, WebLogic, JBoss, Elasticsearch |
| 安全工具    | Burp Suite, SQLMap 的某些模块, ysoserial    |

---

## 关键概念

### 编译与运行

```
.java 源码 → javac 编译 → .class 字节码 → JVM 运行
```

这是 Java 和脚本语言（Python/PHP/JS）最大的区别——需要先编译再运行。`javac` 编译，`java` 执行。

### JVM（Java Virtual Machine）

Java 不直接运行在操作系统上，而是运行在 JVM 上。这带来了"一次编写到处运行"的可移植性，也带来了 JVM 层面的安全考虑（类加载机制、安全管理器）。

### Maven / Gradle

Java 项目的构建和依赖管理工具。`pom.xml`（Maven）或 `build.gradle`（Gradle）的作用类似 Python 的 `requirements.txt`，但更强大。看到 `pom.xml` 就知道这是一个 Java 项目。

### 常见文件后缀

| 后缀 | 说明 |
|------|------|
| `.java` | 源码文件 |
| `.class` | 编译后的字节码文件（可被反编译回 `.java`） |
| `.jar` | 打包的 Java 应用/库（本质是 zip） |
| `.war` | Web 应用打包（Tomcat 部署用） |
| `.jsp` | Java Server Pages——类似 PHP，嵌在 HTML 中的 Java 代码 |
| `pom.xml` | Maven 项目描述文件 |
| `build.gradle` | Gradle 项目描述文件 |

### 注解（Annotation）

Java 中 `@` 开头的标记，大量用于框架：

```java
@Override              // 标记覆盖父类方法
@GetMapping("/api")    // Spring 路由注解
@Autowired             // Spring 自动注入
@RestController        // Spring REST 控制器
```

看到大量 `@` 符号大概率是 Java + Spring 项目。

---

## 安全相关

### Java 反序列化（最著名的 Java 漏洞类型）

Java 反序列化和 PHP 反序列化原理相似但利用链更复杂：

```
攻击者构造恶意序列化对象 → 目标应用反序列化 → 执行任意代码
```

著名工具 **ysoserial** 收集了各种利用链（CommonCollections, Spring 等），看到 Java 应用就要想到反序列化风险。

```java
// 危险做法
ObjectInputStream ois = new ObjectInputStream(userInputStream);
Object obj = ois.readObject();      // 反序列化用户可控数据 → RCE

// 涉及接口：Serializable
class MyData implements Serializable { ... }
```

### 常见 Java 漏洞

| 漏洞类型 | 说明 | 著名案例 |
|----------|------|---------|
| 反序列化 | 恶意序列化数据导致 RCE | WebLogic, JBoss, Jenkins |
| Log4Shell | Log4j2 JNDI 注入导致 RCE | CVE-2021-44228, CVSS 10.0 |
| Spring4Shell | Spring 框架 RCE | CVE-2022-22965 |
| Fastjson | JSON 反序列化绕过 | 多个 CVE |
| JNDI 注入 | 通过命名服务加载远程恶意类 | 常配合 Log4j |

### Spring Boot Actuator

Spring Boot 有一个监控端点叫 Actuator，如果暴露在公网会泄露大量信息：

```
/actuator/env       # 环境变量（可能含密码）
/actuator/mappings  # 所有 API 路由
/actuator/heapdump  # 堆内存快照（可从中提取密钥）
```

---

## Java vs 其他语言

| | Java | Python | JavaScript |
|---|------|--------|------------|
| 类型 | 静态强类型 | 动态强类型 | 动态弱类型 |
| 运行方式 | JVM 字节码 | 解释执行 | JIT 编译（Node/V8） |
| 执行速度 | 快 | 慢 | 快（V8 引擎） |
| 语法风格 | 冗长、显式 | 简洁、可读 | 灵活、函数式 |
| 主要阵地 | 企业后端、Android | 脚本、安全工具、AI | 浏览器、全栈 Web |

---

## 简单总结

- **编译 + JVM 运行**：不是脚本语言，需要 `javac` 编译
- **强类型**：每个变量都要声明类型（或写 `var`）
- **`.jar` 是 Java 的包格式**：可以解压（zip），可以反编译（jd-gui）
- **Spring 框架统治企业 Java**：看到 `@Autowired`、`pom.xml` 就知道是 Spring 项目
- **反序列化是主要攻击面**：ysoserial、Fastjson、Log4j 三条线
