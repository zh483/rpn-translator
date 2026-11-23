# Day 02 任务卡 · 2026-11-24（周二）· 语法 2/2 + 项目第一批代码

> 上午学习、晚上写码。**时间盒 60–75 分钟**。
> 今晚交付第一批项目代码（3 个文件，比练习还简单），这是 M1 的起点。

## 一、学习部分（30 分钟）

| 步骤 | 内容 | 时间 |
| --- | --- | --- |
| 1 | [语法速成](Java语法速成-给C++程序员.md) **§5 控制流 + §6 方法** | 10 分钟 |
| 2 | **§7 类与封装 + §8 继承/接口/多态**（重点：`implements` 多实现、`@Override`） | 15 分钟 |
| 3 | **§9 record 与 enum**（逐字读，今晚要用） | 5 分钟 |

练习 3（集合与栈）如果时间紧，**挪到明晚**，不阻塞交付。

## 二、交付部分（30–40 分钟，3 个文件）

### 1. `src\rpn\TokenType.java`

`public enum TokenType`，成员按顺序：`NUM, PLUS, MINUS, STAR, SLASH, PERCENT, LPAREN, RPAREN, EOF`。

要求：类级 Javadoc 一句话说明"词法单元的类型"；每个常量不需要单独注释。

### 2. `src\rpn\Token.java`

```java
public record Token(TokenType type, String text, int pos, double value) { }
```

要求：
- 类级 Javadoc 说明四个分量各自含义（`text` 保留原文用于回显，`pos` 是 0 基下标，`value` 仅 `NUM` 有意义）
- 用**紧凑构造器**做一条校验：`pos >= 0`，否则抛 `IllegalArgumentException`（§9 有写法）
- **不要**手写 getter（record 自动生成 `type()` 这样的访问器，不是 `getType()`）

### 3. `src\rpn\CompileException.java`

`public class CompileException extends RuntimeException`：
- 内部 `public enum Kind { LEX, SYNTAX, RUNTIME }`
- 字段：`Kind kind`、`int pos`（都 `private final`）
- 构造器：`CompileException(Kind kind, int pos, String message)`，**在 `super(...)` 里拼好最终消息**：`[词法错误] 第 n 个字符：<message>`（注意 `pos` 内部 0 基、显示时 +1）
- 访问器：`kind()`、`pos()`

## 三、验收（自己先跑一遍）

写 `src\rpn\Practice2b.java` 临时验证（用完删）：

```java
Token t = new Token(TokenType.NUM, "3.14", 2, 3.14);
System.out.println(t);                          // Token[type=NUM, text=3.14, pos=2, value=3.14]
System.out.println(t.value());                  // 3.14
try {
    throw new CompileException(CompileException.Kind.LEX, 1, "非法字符 '$'");
} catch (CompileException e) {
    System.out.println(e.getMessage());         // [词法错误] 第 2 个字符：非法字符 '$'
    System.out.println(e.pos());                // 1
}
try {
    new Token(TokenType.EOF, "", -1, 0);
} catch (IllegalArgumentException e) {
    System.out.println("校验生效: " + e.getMessage());
}
```

**必须全部符合预期**，特别是：`toString()` 是 record 自动给的、`pos` 显示是 2 而内部是 1。

## 四、硬性约束（违反打回）

- [ ] 三个文件都在 `package rpn;`
- [ ] 文件名与 public 类型名**完全一致（含大小写）**
- [ ] 无 `import java.awt` / `javax.swing` / `com.sun.net.httpserver`
- [ ] 每个 public 类/记录/构造器有 Javadoc
- [ ] 不用魔法数字（位置基准 0/1 的转换只出现在 `CompileException` 构造器里）

## 五、交付给我什么

1. 编译命令 + 运行输出**原文**
2. commit 号

```bat
git add src/rpn/TokenType.java src/rpn/Token.java src/rpn/CompileException.java
git commit -m "feat: Token/TokenType 数据模型与统一异常"
```

## 六、明晚预告（Day 03）

`Lexer.scan()`：跳过空白、识别数字（含整数/小数）、识别 8 个单字符运算符、非法字符抛 `CompileException`；先用 4 条基础用例验证。
