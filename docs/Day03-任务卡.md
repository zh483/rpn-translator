# Day 03 任务卡 · 2026-11-25（周三）· 词法分析器主体

> **时间盒 60–75 分钟**。今天是本项目第一段真正的编译逻辑。
> 昨天那 3 个数据类必须已经编译通过并能被引用。

## 一、目标

`src\rpn\Lexer.java`：

```java
public class Lexer {
    /** 扫描整个输入串，返回记号序列（末尾总有一个 EOF）。 */
    public List<Token> scan(String src) { ... }
}
```

本轮只要求支持：
1. 跳过空白（空格、`\t`、`\r`、`\n` 都跳过）
2. 数字：`12`、`3.14`、`.5`、`5.`
3. 8 个单字符：`+ - * / % ( )`
4. 非法字符：抛 `CompileException(Kind.LEX, pos, "非法字符 'x'")`
5. 末尾追加 `Token(TokenType.EOF, "", src.length(), 0)`

## 二、实现建议（思路，不是代码）

1. 先写一个 `int i = 0;` 的循环，`while (i < src.length())`。
2. 每次循环先做三选一：**空白 → 数字 → 运算符**（顺序别反）。
3. 数字分支：记下 `start = i`，连续吞掉数字，再处理可选的小数点与后续数字，最后 `String text = src.substring(start, i)` → `Double.parseDouble(text)` → `new Token(TokenType.NUM, text, start, value)`。
4. 运算符分支：用 `switch (c)` 映射到 `TokenType`，每个 case 里 `new Token(type, String.valueOf(c), i, 0)`，别忘了 `i++`。
5. 非法字符：直接 `throw new CompileException(CompileException.Kind.LEX, i, "非法字符 '" + c + "'")`。

**几个容易写错的地方**：
- 别在数字分支里用 `Double.parseDouble` 去"试"边界（`1.2.3` 会抛 `NumberFormatException` 而不是你的词法错误）
- `i` 的自增位置：每个分支负责把 `i` 推到下一个未扫描字符
- `.5` 与 `5.` 都要能识别：`5.` 解析成 `5.0` 是合法 Java 写法；`.5` 需要先判断"`.` 后面紧跟数字"

## 三、验收用例（4 条基础，先过这 4 条）

| # | 输入 | 期望 |
| --- | --- | --- |
| 1 | `12` | `NUM(12.0) EOF` |
| 2 | `3.14` | `NUM(3.14) EOF` |
| 3 | `1+2` | `NUM(1) PLUS NUM(2) EOF` |
| 4 | `1 + 2` | 同上（空白被跳过） |

自测时临时写个 `main` 打印每个 token 的 `type()/text()/pos()`，跑完删掉。**明晚再写正式的 `TestRunner`。**

## 四、硬性约束

- [ ] `Lexer` 不持有可变静态字段；`scan` 可重复调用
- [ ] 不改输入串、不用全局变量传状态
- [ ] 所有 token 的 `pos` 是该记号在原串中的**起始**下标（0 基）
- [ ] 异常消息含"第 n 个字符"（由 `CompileException` 统一拼）
- [ ] public 类与 public 方法有 Javadoc

## 五、交付

1. 4 条用例的真实输出
2. commit：`feat: 词法分析器扫描数字与单字符运算符`

## 六、明晚预告（Day 04）

边界：`.5`、`5.`、`1.2.3`、`1..2`、`(1+2`、空串、只有空白；补齐到 7 条用例并全部通过。
