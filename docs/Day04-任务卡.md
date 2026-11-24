# Day 04 任务卡 · 2026-11-25（周三）· 边界规则 + TestRunner + M1

> **时间盒 60–75 分钟**。今天的目标不是写新功能，而是把词法器**钉死**：修 3 个边界、写 16 条用例、让测试替你做回归。
> 做完这一步，里程碑 **M1（词法全绿）** 提前达成。

## 一、先修 3 个边界（15 分钟）

### 边界 1：全角数字会崩（P0）

实测：`scan("１+２")` → `NumberFormatException: For input string: "１"`（未捕获，直接崩）。

原因：`Character.isDigit('１')` 返回 **true**（全角数字也是 Unicode 数字），于是进入数字分支；但 `Double.parseDouble("１")` 抛异常。

**修法**：数字判断从"Unicode 数字"收紧为"ASCII 数字"，两处都要改：

```java
// 起点判断
else if ((c >= '0' && c <= '9') || c == '.')
// 循环条件
while ((c >= '0' && c <= '9') || (c == '.' && !havepot))
```

改完全角数字会落到 `default` 分支 → `[词法错误] 第 1 个字符: 非法字符: '１'`，这才是正确行为。

### 边界 2：数字后紧跟点（`1.2.3`、`1..2`）

现在的结果：`1.2.3` → `NUM(1.2)` + `NUM(.3)`；`1..2` → `NUM(1.)` + `NUM(.2)`。不崩，但语义错了——两个数字挨着没有运算符，这是**词法层面就该拒绝**的畸形数字，不该留给语法分析器去猜。

**规则**：数字扫描结束后，若下一个字符是 `'.'`，抛词法错误。

```java
// 在 tokens.add(NUM...) 之后、continue 之前
if (i < src.length() && src.charAt(i) == '.') {
    throw new CompileException(CompileException.Kind.LEX, start, "非法数字: " + src.substring(start, i + 1));
}
```

注意 `5.` 依然合法（点在第一段就被消费掉了，不会走到这个判断）。

### 边界 3：括号不匹配归语法层

`(1+2` 在**词法层不报错**：正常返回 `LPAREN NUM PLUS NUM EOF`，由 `Parser` 报"期望 ')'"。

不要在词法层数括号——那是语法规则，词法层只认字符。

## 二、写 TestRunner（30 分钟）

### 设计要求

- 一个主类 `TestRunner`，`main` 里跑完三组用例
- 输出表格：`编号 | 输入 | 期望 | 实际 | PASS/FAIL`
- 结尾输出 `通过 x / 失败 y`；**有失败就 `System.exit(1)`**
- 一个辅助方法把 token 流渲染成**固定格式字符串**，方便断言比较：

```
NUM(12)@0 PLUS(+)@1 NUM(3)@2 EOF@5
```

### 16 条用例

**合法组（10 条）**

| 编号 | 输入 | 期望 |
| --- | --- | --- |
| L01 | `1` | `NUM(1)@0 EOF@1` |
| L02 | `12` | `NUM(12)@0 EOF@2` |
| L03 | `3.14` | `NUM(3.14)@0 EOF@4` |
| L04 | `.5` | `NUM(.5)@0 EOF@2` |
| L05 | `5.` | `NUM(5.)@0 EOF@2` |
| L06 | `1+2*3` | `NUM(1)@0 PLUS(+)@1 NUM(2)@2 STAR(*)@3 NUM(3)@4 EOF@5` |
| L07 | `(1+2)*3` | `LPAREN(()@0 NUM(1)@1 PLUS(+)@2 NUM(2)@3 RPAREN())@4 STAR(*)@5 NUM(3)@6 EOF@7` |
| L08 | `1 + 2` | `NUM(1)@0 PLUS(+)@2 NUM(2)@4 EOF@5` |
| L09 | `8/4%3` | `NUM(8)@0 SLASH(/)@1 NUM(4)@2 PERCENT(%)@3 NUM(3)@4 EOF@5` |
| L10 | （空串） | `EOF@0` |

**错误组（6 条）**

| 编号 | 输入 | 期望 |
| --- | --- | --- |
| E01 | `1$a` | `[词法错误] 第 2 个字符` |
| E02 | `.` | `[词法错误] 第 1 个字符` |
| E03 | `1.2.3` | `[词法错误] 第 4 个字符` |
| E04 | `1..2` | `[词法错误] 第 3 个字符` |
| E05 | `12ab` | `[词法错误] 第 3 个字符` |
| E06 | `１+２`（全角） | `[词法错误] 第 1 个字符` |

> 位置全部是 **1 基**（跟用户看到的字符序号一致）。错误断言只比较"类别 + 第 n 个字符"这两个关键信息，不比对完整消息文本——消息措辞会变，位置和类别不该变。

### 实现提示

```java
/** 把 token 流渲染成断言用的固定格式：TYPE(text)@pos 以空格分隔。 */
private static String render(List<Token> tokens) { ... }

/** 期望抛词法错误：类别 + 1 基位置。 */
private static void expectError(String id, String src, int pos1Based) { ... }
```

## 三、验收

```bat
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d out\classes src\rpn\*.java
"%JAVA_HOME%\bin\java" -cp out\classes rpn.TestRunner
```

三个条件同时满足才算完：

- [ ] `check.bat` 输出 **0 FAIL**（`TestRunner` 也要 Javadoc）
- [ ] `TestRunner` 输出 **16/16 PASS**
- [ ] commit：`test: 词法用例 16 条与 TestRunner；修全角数字与小数点边界`

## 四、完成后

**M1 达成**（原计划 11/27，提前 2 天）。剩下的 W12 时间可以：

1. 把 `Lexer` 里两条超 100 字符的行拆掉（门禁 WARN 清零）
2. 预习 [Java 语法速成 §9–§10](../docs/Java语法速成-给C++程序员.md)（record/enum/异常）——`Parser` 要用
3. 提前开始 Day 05：`Parser` 的 `expr()/term()/factor()` 骨架（明天正式发卡）
