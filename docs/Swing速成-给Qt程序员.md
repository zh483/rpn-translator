# Swing 速成（写给会 Qt 的人）

> 目标：2 小时写出单窗口桌面应用。你 Qt 的底子（控件树、布局、信号槽、事件循环）几乎全部可迁移，
> 真正的差异只有两处：**信号槽 → 监听器**、**事件循环 → EDT（单线程）**。

---

## §0 心智模型：三句话对齐

| Qt | Swing |
| --- | --- |
| QWidget 树（父子关系管理生命周期） | JComponent 树（`add()` 进容器即挂上） |
| 信号槽（`connect`） | 监听器（`addActionListener` / `addDocumentListener`） |
| 事件循环 `app.exec()` | 自动启动的 **EDT**（Event Dispatch Thread），你不写 exec |
| QSS 样式表 | 几乎等价物（LookAndFeel + 少量 HTML），**不要指望 QSS 级别的定制** |

最重要的一条：**Swing 所有界面操作必须在 EDT 上做**。你 Qt 里"UI 线程不能阻塞"的直觉是对的，但 Swing 更严格——连 `setText` 都算界面操作。

---

## §1 控件对照表（够用版）

| Qt | Swing | 备注 |
| --- | --- | --- |
| `QApplication` | 无 | Swing 不需要显式创建应用对象 |
| `QMainWindow` / `QWidget` | `JFrame` / `JPanel` | JFrame 是顶层窗口，JPanel 是容器 |
| `QLabel` | `JLabel` | 只读文本 |
| `QLineEdit` | `JTextField` | 单行输入 |
| `QPlainTextEdit` / `QTextEdit` | `JTextArea` | 多行文本；`setEditable(false)` 当输出用 |
| `QPushButton` | `JButton` | |
| `QMessageBox` | `JOptionPane.showMessageDialog` | |
| `QHBoxLayout` | `BoxLayout(X_AXIS)` 或 `FlowLayout` | |
| `QVBoxLayout` | `BoxLayout(Y_AXIS)` | |
| `QGridLayout` | `GridLayout(rows, cols)` | |
| `QFormLayout` | 无 | 用 `GridLayout` 两列 + `JLabel` |
| `setFixedSize` / `resize` | `setSize` / `setPreferredSize` | 布局管理器说了算 |
| `setWindowTitle` | `setTitle` | |
| `move(x, y)` | `setLocation(x, y)` | |
| `connect(btn, &QPushButton::clicked, ...)` | `btn.addActionListener(e -> {...})` | 接口 + lambda |
| `ui.xxx->setText(s)` | `label.setText(s)` | |
| `delete widget` | 不用管（GC + 容器移除） | 但要 `remove(...)` 从容器摘掉 |
| `app.exec()` | 无 | 窗口显示后自动进入事件循环 |

文本换行/多行显示：`JTextArea` 需要 `setLineWrap(true)`；`JLabel` 用 HTML 可以换行（`<html>...<br>...`）。

---

## §2 最小窗口（20 行，看懂结构即可）

```java
import javax.swing.*;

public class Demo {
    public static void main(String[] args) {
        // 所有界面创建放 EDT 里（等价于 Qt 创建 QApplication 后 exec 之前的阶段）
        SwingUtilities.invokeLater(() -> {
            JFrame f = new JFrame("最小窗口");
            f.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);   // 关窗口就退出
            f.setLayout(new java.awt.BorderLayout());

            JTextField input = new JTextField();
            JButton run = new JButton("计算");
            JLabel out = new JLabel("等待输入");

            run.addActionListener(e -> out.setText("你输入了: " + input.getText()));

            f.add(input, java.awt.BorderLayout.NORTH);
            f.add(run, java.awt.BorderLayout.CENTER);
            f.add(out, java.awt.BorderLayout.SOUTH);
            f.setSize(420, 200);
            f.setVisible(true);
        });
    }
}
```

和 Qt 的差别一眼可见：**没有 `exec()`**、**没有 `Q_OBJECT`**、**没有信号声明**，回调就是一个 lambda。

---

## §3 你的 `SwingShell` 该怎么组装（三层嵌套，别上 GridBagLayout）

```
JFrame (BorderLayout)
├─ NORTH : JPanel(FlowLayout)      ← 「表达式：」JLabel + JTextField + 计算按钮 + 清空按钮
├─ CENTER: JPanel(GridLayout(1,3)) ← 三栏：中缀式 / 逆波兰式 / 计算结果
│           每栏是 JPanel(BorderLayout)：NORTH 标题 JLabel，CENTER 只读 JTextArea
└─ SOUTH : JLabel                  ← 错误提示（红字），或"就绪"灰字
```

组装顺序（每步都能跑起来看效果）：

1. 建 `JFrame`，`setTitle`、`setDefaultCloseOperation`、`BorderLayout`
2. 做 NORTH 面板：输入框 + 两个按钮，`addActionListener`
3. 做 CENTER 面板：三个小面板，各放标题 + 只读文本区
4. 做 SOUTH 错误行
5. 按钮回调里：`new RpnService().evaluate(输入)` → 成功就三个区 `setText`，失败 catch `CompileException` 把 `getMessage()` 刷到错误行（红字，成功后清空）

**回调里不要写编译逻辑**，只调 `RpnService`——这是分层，报告 2.3.5 会写。

---

## §4 五个必踩的坑

| # | 坑 | 现象 | 解决 |
| --- | --- | --- | --- |
| 1 | 忘了 `setVisible(true)` | 窗口不出现 | 最后一行必须调 |
| 2 | 只 `setSize` 不 `setLayout` | 控件全叠在一起 / 只有一个可见 | 顶层用 `BorderLayout`，子面板各自设布局 |
| 3 | 中文显示成方块 | 字体缺中文字形 | `new Font("Microsoft YaHei", Font.PLAIN, 14)` 设到控件上，或全局 `UIManager` |
| 4 | 关窗口进程不退 | 事件循环还在 | `setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE)` |
| 5 | 在回调里 `Thread.sleep` / 长循环 | 界面卡死 | 计算要快（我们 <1ms）；真耗时再开线程 + `invokeLater` 回 EDT |

---

## §5 与 Qt 三个"思维差异"

1. **没有信号声明**：Qt 用 `signals:` + moc；Swing 用接口 + lambda，好处是随便写、坏处是没有编译期检查（拼错方法名只会静默不触发——所以监听器注册后先随便点一下验证）。
2. **布局是"建议"**：`setPreferredSize` 只是建议，最终由 LayoutManager 决定。Qt 的 `setFixedSize` 语义更硬。
3. **样式能力弱**：QSS 能干的事，Swing 基本只能靠 LookAndFeel（可选 FlatLaf）或自绘。**别在界面上花太多时间**，报告看重的是功能正确 + 结果清晰。

---

## §6 验收清单（界面做完对着勾）

- [ ] 双击 `run.bat` 能弹出窗口（不是浏览器）
- [ ] 输入 `1+2*3` → 中缀 `1+2*3` / RPN `1 2 3 * +` / 结果 `7`
- [ ] 输入 `0.1+0.2` → 结果 `0.3`（验证格式化生效）
- [ ] 输入 `8/(2-2)` → 错误行红字：`[运行时错误] 第 2 个字符: 不能除0`
- [ ] 输入 `1+` → 错误行红字：`[语法错误] 第 3 个字符: …`
- [ ] 点"清空"→ 输入框与三个结果区都清空
- [ ] 窗口固定大小、标题正确、关闭即退出
- [ ] 截两张图（正常态 / 错误态）供报告 图3-1、图3-2
