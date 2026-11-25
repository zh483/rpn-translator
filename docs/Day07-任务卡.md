# Day 07 任务卡 · 展示层：ResultFormatter + RpnService 门面

> **时间盒 45–60 分钟**。目标：把"表达式字符串 → 可显示的结果"封装成一次调用，为界面做准备。
> 今天不碰界面，只把**业务侧最后两块**补齐：格式化与门面。

## 一、`ResultFormatter`（约 20 分钟）

```java
public final class ResultFormatter {
    /** 把求值结果格式化为可显示文本。 */
    public static String format(double value) { ... }
}
```

规则（对应 ADR-003）：

| 情况 | 输出 | 例 |
| --- | --- | --- |
| 与最近整数差 < 1e-9 | 整数形式 | `7.0` → `7`；`3.0000000001` → `3` |
| 其它有限数 | 最多 10 位有效数字、去尾零 | `0.1+0.2` → `0.3`；`1/3` → `0.3333333333` |
| `-0.0` | `0`（先归一化） | `-0.0` → `0` |
| `NaN` | `NaN` | —— |
| `±Infinity` | `Infinity` / `-Infinity` | 溢出时兜底，不让界面崩 |

实现提示：整数判定用 `Math.abs(v - Math.rint(v)) < 1e-9`；整数输出用 `String.format("%.0f", v)`（不要 `(long) v`，大数会饱和）；非整数用 `String.format("%.10g", v)`。`-0.0` 记得 `v == 0 ? 0.0 : v`。

## 二、`RpnService` 门面（约 20 分钟）

```java
public final class RpnService {
    /**
     * 一次调用完成：词法分析 → 语法分析（生成后缀序列）→ 求值 → 格式化。
     *
     * @param expression 中缀表达式
     * @return 结果快照（含原文、后缀文本、结果文本）
     * @throws CompileException 词法/语法/运行时错误
     */
    public RpnResult evaluate(String expression) { ... }
}
```

配套一个不可变结果对象（record）：

```java
public record RpnResult(String expression, String rpnText, String valueText) { }
```

- `rpnText`：把后缀序列的 `text()` 用空格连接，例如 `1 2 3 * +`
- `valueText`：`ResultFormatter.format(eval 结果)`，例如 `7`
- 出错时**直接抛** `CompileException`，由界面层捕获并显示 `getMessage()`（消息已含类别与位置）

**这一层的意义**：界面代码（Web 前端 / Swing 壳 / 测试）都只认识 `RpnService.evaluate`，谁也不知道里面有几个类。将来换求值策略、加缓存，界面一行都不用改。

## 三、接进 TestRunner（约 15 分钟）

新增 `testdata/formatcases.txt`，验证"表达式 → 显示文本"的全链路：

| 编号 | 输入 | 类型 | 期望显示 |
| --- | --- | --- | --- |
| F01 | `1+2*3` | FOK | `7` |
| F02 | `(1+2)*3` | FOK | `9` |
| F03 | `2.5+0.5` | FOK | `3` |
| F04 | `0.1+0.2` | FOK | `0.3` |
| F05 | `1/3` | FOK | `0.3333333333` |
| F06 | `-2*3` | FOK | `-6` |
| F07 | `2--3` | FOK | `5` |
| F08 | `1+` | FERR | `2`（语法错误位置，0 基） |
| F09 | `8/(2-2)` | FERR | `1`（运行时错误位置，0 基） |

TestRunner 里加第四组 `runFormatCases()`：`FOK` 比对 `RpnResult.valueText()`；`FERR` 捕获异常比对类别与位置。

## 四、验收

- [ ] 上述 9 条格式/门面用例全部通过
- [ ] 原有 51 条用例不回归（`java ... TestRunner` 仍全绿）
- [ ] `check.bat` → 0 FAIL
- [ ] commit：`feat: 结果格式化与 RpnService 门面`

## 五、做完之后

界面阶段的三条线（Day 08+）：

1. `WebApi`（`com.sun.net.httpserver`）+ `web/` 单页 → 主界面
2. `SwingShell`（80 行）→ 桌面兜底
3. `Main` 入口 + `run.bat` 联调 → 现场可演示

报告同步（**等界面做完再动**）：
- 3.2 表3-1 换成真实用例（从 `testdata/*.txt` 抽）
- 3.3 图3-1/3-2 换成真实截图
- 2.3.2–2.3.4 代码片段换成真实代码
- 4.1/4.2 补到 600 字（作者本人续写）

## 六、注意

- `ResultFormatter` 与 `RpnService` 都属于**核心层**：不得 import 界面/网络类（门禁会检查）
- 两个类都要有类级 Javadoc 和 public 方法 Javadoc（门禁 FAIL 项）
- 别把格式化逻辑写进 `Evaluator`——那是展示层职责，求值器只返回 `double`
