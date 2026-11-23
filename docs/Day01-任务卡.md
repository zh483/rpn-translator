# Day 01 任务卡 · 2026-11-23（周一）· **学习日，不交付代码**

> 今天只有一件事：把 Java 语法从"完全不会"推到"看得懂、能改、能写小程序"。
> 时间盒 **45–60 分钟**，做完就停，不写项目代码。

## 今晚做什么（按顺序，别跳）

| 步骤 | 内容 | 时间 | 卡住时回查 |
| --- | --- | --- | --- |
| 1 | 读 [Java语法速成-给C++程序员.md](Java语法速成-给C++程序员.md) 的 **§0 心智模型** | 8 分钟 | —— |
| 2 | 读 **§1 最小程序与工具链**，然后做 **练习 1** | 12 分钟 | §15 报错翻译表 |
| 3 | 读 **§2 类型系统 + §3 字符串**，然后做 **练习 2** | 25 分钟 | 练习 2 的折叠答案 |
| 4 | 读 **§4 数组与集合**（只看 List / Deque / Map 三段） | 10 分钟 | —— |

**§5 之后（控制流/类/继承/record/异常）明晚再读**，今晚不需要。

## 练习 1：跑通工具链（12 分钟）

写 `src/rpn/Practice1.java`：打印参数个数和每个参数。

```java
package rpn;

public class Practice1 {
    public static void main(String[] args) {
        System.out.println("参数个数: " + args.length);
        for (String a : args) {
            System.out.println("参数: " + a);
        }
    }
}
```

```bat
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d out\classes src\rpn\Practice1.java
"%JAVA_HOME%\bin\java" -cp out\classes rpn.Practice1 a b
```

**期望输出**：参数个数 2、参数 a、参数 b。

## 练习 2：类型与字符串（25 分钟，重点是"猜错"的那些）

写 `src\rpn\Practice2.java`，把 [语法速成 §14 练习 2](Java语法速成-给C++程序员.md#练习-220-分钟类型与字符串) 里那 7 行打印出来。

**要求**：先把答案写在纸上/注释里，再运行对照。**猜错的每一行都是你明天的薄弱点**，猜错哪行就把对应小节重读一遍。

## 交付给我什么

1. 练习 1 的真实输出
2. 练习 2 的 7 行输出 + **你猜错了几行**
3. 一句话：今晚哪个概念最反直觉

> 不用 commit 练习文件（练习不进入项目代码，明晚我会让你把它们删掉）。

## 明晚预告（Day 02）

读 §5–§8（控制流 / 方法 / 类 / 继承与接口）+ 练习 3，然后写项目第一批真实代码：`TokenType`（enum）+ `Token`（record）+ `CompileException`（自定义异常）—— 这三个文件就是今晚 §9–§10 的直接应用。
