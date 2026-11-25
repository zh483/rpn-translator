# Day 08 任务卡 · SwingShell：桌面主界面（分步版）

> **时间盒 90–120 分钟**。今天只做一件事：**双击 `run.bat` 弹出一个能算表达式的窗口**。
> 原则：**每一步都要能运行看效果**，不要一口气写完再跑。
> 配套材料：[Swing速成-给Qt程序员.md](Swing速成-给Qt程序员.md)（§1 对照表、§3 组装顺序、§4 坑、§6 验收）

## 交付物

| 文件 | 作用 |
| --- | --- |
| `src/rpn/SwingShell.java` | 主窗口（界面 only，不写编译逻辑） |
| `src/rpn/Main.java` | 入口：`SwingUtilities.invokeLater(...)` 启动窗口 |
| `run.bat`（改） | 去掉"打开浏览器"，改为直接跑 `rpn.Main` |
| `src/rpn/TestRunner.java`（改） | 增加第四组：`testdata/formatcases.txt` |
| 两张截图 | 正常态 + 错误态，供报告 图3-1/3-2 |

---

## Step 0｜先读 10 分钟

- 教程 §1（控件对照）、§3（三层嵌套结构）、§4（五个坑）
- 记住一句：**Swing 的界面操作都在 EDT 上，入口用 `SwingUtilities.invokeLater`**

---

## Step 1｜空窗口（约 15 分钟）

目标：出现一个 640×420 的空白窗口，标题正确，点 × 能退出。

- 继承：`public class SwingShell extends JFrame`（简单直接）
- 构造器里：`setTitle("算术表达式翻译与求值系统")`、`setSize(640, 420)`、`setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)`、`setLayout(new BorderLayout())`
- 这一版先 `setVisible(true)` 放在构造器末尾（等 `Main` 写好后再挪走）

**Qt 对照**：`QMainWindow` 的 `setWindowTitle/setFixedSize/close` 三件套。

**卡住判断**：窗口不出现 → 99% 是没 `setVisible(true)`，或 `Main` 没跑起来。

---

## Step 2｜输入行（NORTH，约 15 分钟）

```
JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
top.add(new JLabel("表达式："));
top.add(inputField);        // JTextField，setColumns(20)
top.add(calcButton);        // "翻译并求值"
top.add(clearButton);       // "清空"
add(top, BorderLayout.NORTH);
```

**Qt 对照**：`QHBoxLayout` + `QLabel` + `QLineEdit` + `QPushButton`。

**本步验收**：窗口顶部出现四个控件，输入框能打字。

---

## Step 3｜三栏结果区（CENTER，约 20 分钟）

```
JPanel center = new JPanel(new GridLayout(1, 3, 8, 8));   // 1 行 3 列，间距 8
center.add(makePanel("中缀表达式", infixArea));
center.add(makePanel("逆波兰式",  rpnArea));
center.add(makePanel("计算结果",  valueArea));
add(center, BorderLayout.CENTER);
```

`makePanel(String title, JTextArea area)`：返回一个 `JPanel(BorderLayout)`，`NORTH` 放标题 `JLabel`，`CENTER` 放 `JScrollPane(area)`。

三个 `JTextArea`：`setEditable(false)`、`setLineWrap(true)`；RPN 区建议 `setFont(new Font("Consolas", Font.PLAIN, 16))`。

**Qt 对照**：`QGridLayout` + 三个 `QGroupBox`。

**本步验收**：三栏等宽排列，标题清楚，能显示空文本。

---

## Step 4｜错误行（SOUTH，约 5 分钟）

```
errorLabel = new JLabel("就绪");
errorLabel.setForeground(Color.GRAY);
add(errorLabel, BorderLayout.SOUTH);
```

成功/中性状态用灰色，出错时 `setForeground(new Color(192, 0, 0))`。

**Qt 对照**：一个 `QLabel`，`setStyleSheet("color:#c00000")`。

---

## Step 5｜接 `RpnService`（约 20 分钟，核心一步）

按钮监听器里**只做三件事**：取值 → 调服务 → 显示：

```
calcButton.addActionListener(e -> {
    String expr = inputField.getText() == null ? "" : inputField.getText().strip();
    try {
        RpnResult r = service.evaluate(expr);     // RpnService.RpnResult（嵌套类型）
        infixArea.setText(r.expression());
        rpnArea.setText(r.rpnText());
        valueArea.setText(r.valueText());
        errorLabel.setText("就绪");
        errorLabel.setForeground(Color.GRAY);
    } catch (CompileException ex) {
        errorLabel.setText(ex.getMessage());       // 消息已含类别 + 位置
        errorLabel.setForeground(new Color(192, 0, 0));
        rpnArea.setText("—");
        valueArea.setText("—");
    }
});
```

**纪律**：监听器里**不许出现 Token/Lexer/Parser/Evaluator** 这些词——界面只认识 `RpnService`（报告 2.3.5 会写这条分层）。

**Qt 对照**：`connect(btn, &QPushButton::clicked, this, [=]{ ... })`，逻辑一模一样。

**本步验收**：输入 `1+2*3` 点按钮 → 三栏分别是 `1+2*3` / `1 2 3 * +` / `7`。

---

## Step 6｜清空 + 外观（约 10 分钟）

- 清空按钮：`inputField.setText("")`、三个区 `setText("")`、错误行复位成灰色"就绪"
- 字体：中文控件统一 `new Font("Microsoft YaHei", Font.PLAIN, 14)`（防方块）
- 可选：`inputField.addActionListener(...)` 让回车等于点按钮

---

## Step 7｜`Main` 入口 + `run.bat`（约 10 分钟）

```java
public class Main {
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SwingShell().setVisible(true));
    }
}
```

然后把 `SwingShell` 构造器里的 `setVisible(true)` 删掉（由 `Main` 统一控制）。

`run.bat` 改两处：删掉 `start "" http://127.0.0.1:8080`；启动类写成 `java -cp out\classes rpn.Main`。**保持纯 ASCII**（否则 GBK 崩）。

---

## Step 8｜验收清单（对着勾，约 10 分钟）

- [ ] `run.bat` 双击 → 弹窗口（不是浏览器）
- [ ] `1+2*3` → `1+2*3` / `1 2 3 * +` / `7`
- [ ] `0.1+0.2` → 结果 `0.3`（格式化生效）
- [ ] `1/3` → `0.3333333333`
- [ ] `7%2.5` → `2`
- [ ] `8/(2-2)` → 错误行红字 `[运行时错误] 第 2 个字符: 不能除0`
- [ ] `1+` → 错误行红字 `[语法错误] 第 3 个字符: …`
- [ ] `1$a` → 错误行红字 `[词法错误] 第 2 个字符: 非法字符: '$'`
- [ ] 清空按钮工作
- [ ] 截图两张：正常态（`1+2*3`）、错误态（`8/(2-2)`）

---

## Step 9｜TestRunner 第四组（约 15 分钟，可与界面并行）

读 `testdata/formatcases.txt`（11 条，已备好）：

| kind | 断言 |
| --- | --- |
| `FOK` | `new RpnService().evaluate(src).valueText()` 与期望**逐字符相等** |
| `FERR` | 必须抛 `CompileException`，且 `pos()` 与期望相等 |

方法名建议 `runFormatCases()`，与现有三组并列；汇总里加上。

---

## 症状 → 原因 速查表

| 症状 | 原因 | 改法 |
| --- | --- | --- |
| 窗口不出现 | 没 `setVisible(true)` / `Main` 没调 | 补一行 |
| 窗口空白、控件看不见 | 顶层没设 `BorderLayout`，或忘了 `add(..., 位置)` | 检查 `setLayout` 与 `add` 的位置参数 |
| 三个面板挤在一起 | `GridLayout` 的 1×3 写错成 3×1 | `new GridLayout(1, 3)` 是 1 行 3 列 |
| 点按钮没反应 | 监听器没注册 / 方法名拼错（Swing 不报错） | `addActionListener` 后先 `System.out.println` 验证 |
| 界面卡死 | 监听器里干了耗时的事 | 我们不需要线程；删掉 `sleep`/循环 |
| 中文变方块 | 字体没中文字形 | `new Font("Microsoft YaHei", ...)` |
| 关窗口进程不退 | 没设 `EXIT_ON_CLOSE` | 补 |
| 错误消息显示不全 | 用了 `JTextField` 显示长消息 | 错误行用 `JLabel` 且窗口够宽；或改成只读 `JTextArea` |
| `RpnResult` 找不到 | 它是 `RpnService` 的嵌套 record | 写 `RpnService.RpnResult` 或用 `var` |
| `run.bat` 闪退 | 编译错误 / 类名错 / 非 ASCII | 先在终端跑 `java -cp out\classes rpn.Main` 看报错 |

---

## 提交

```
docs: Day08 界面任务卡（分步 + Qt 对照 + 症状速查）
feat: SwingShell 桌面主界面（RpnService 调用、三栏结果、错误定位显示）
chore: Main 入口与 run.bat 改为桌面启动
test: TestRunner 第四组（格式化用例 11 条）
```

## 卡住时怎么问我

贴三样：**哪个 Step**、**现象/报错原文**、**你已经试过的一个改法**。界面问题 90% 落在上面那张速查表里。
