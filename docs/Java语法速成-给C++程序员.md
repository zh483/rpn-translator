# Java 语法速成（写给会 C++ 的人）

> **用法**：不要从头到尾读。先看 §0 的心智模型，然后按 §14 的练习顺序做，卡住再回查对应节。
> **目标**：3 晚达到"能独立写词法分析器"的语法水平。你 C++ 功底够（类、RAII、递归都写过），真正要补的只有：对象模型差异、集合 API、record/enum、异常体系。
> **不要**：看视频教程从"什么是变量"开始学——那会花掉你 10 小时。

---

## §0 心智模型：Java 与 C++ 的 10 个根本差异

| # | C++ | Java | 影响 |
| --- | --- | --- | --- |
| 1 | 栈对象、确定性析构 | **一切对象都在堆上，靠 GC** | 没有析构函数，别把"释放资源"写在 `finalize` |
| 2 | 指针、指针算术 | **只有引用**，无指针算术 | 没有 `*`、`->`、`&`；`null` 就是空引用 |
| 3 | 头文件 + 编译单元 | **一个文件一个 public 类**，无头文件 | 文件名 = public 类名（含大小写） |
| 4 | 方法默认非虚，`virtual` 显式 | **方法默认虚**，可被重写 | 多态天然成立；不想被重写加 `final` |
| 5 | 运算符重载 | **不支持**（`+` 只对 String 特例） | 比较对象必须写 `equals` |
| 6 | 模板（编译期展开） | **泛型（类型擦除）** | `List<int>` 不合法，要 `List<Integer>` |
| 7 | 异常可任意抛 | **checked / unchecked 两套** | 继承 `RuntimeException` 就不必写 `throws` |
| 8 | `const` 全链路 | 只有 `final`（引用不可变，对象仍可变） | `final List` 仍可 `add` |
| 9 | 数组/容器边界不查 | **数组下标必查**，越界抛异常 | 少一类内存错误，多一类异常处理 |
| 10 | 多重继承 | **单继承 + 多接口** | `interface` 是主力，`extends` 只能一个 |

一句话记忆：**Java 是"托管堆 + 引用 + 接口"的世界，写起来比 C++ 啰嗦，但没有内存事故。**

---

## §1 最小程序与工具链

```java
package rpn;                     // 1) 包声明，必须第一行（注释除外），目录要对应 src/rpn/

public class Hello {             // 2) 文件名必须是 Hello.java（含大小写）

    public static void main(String[] args) {   // 3) 入口签名固定，void 不能省
        System.out.println("Hello 你好，JDK " + System.getProperty("java.version"));
    }
}
```

编译运行（在项目根目录）：

```bat
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d out\classes src\rpn\Hello.java
"%JAVA_HOME%\bin\java" -cp out\classes rpn.Hello
```

- `-d out\classes`：输出目录（按包名自动建子目录 `out\classes\rpn\Hello.class`）
- `-encoding UTF-8`：**不写这个，中文注释会报"非法字符"**
- `-cp`（classpath）：告诉 JVM 去哪找 `.class`；运行时要写**全限定名** `rpn.Hello`（不是路径）

常用输出：

```java
System.out.println("a");          // 换行
System.out.print("a");            // 不换行
System.out.printf("%.2f%n", 3.14159);  // 格式化，%n 是换行
System.out.println(1 / 3);        // 0   ← 整数除法
System.out.println(1.0 / 3);      // 0.3333333333333333
```

---

## §2 类型系统

8 种基本类型（**没有 unsigned**）：

| 类型 | 字节 | 范围/说明 |
| --- | --- | --- |
| `byte` | 1 | -128~127 |
| `short` | 2 | ±3.2 万 |
| `int` | 4 | ±21 亿（默认整数类型） |
| `long` | 8 | 字面量加 `L`：`10L` |
| `float` | 4 | 字面量加 `f`：`1.5f` |
| `double` | 8 | **默认小数类型**（本项目数值都用它） |
| `char` | 2 | **16 位 Unicode**（不是 8 位！可存中文） |
| `boolean` | 1 | 只有 `true`/`false`，**不能和 int 互转** |

```java
int count = 0;
long size = 10L;
double v = 3.14;
char c = '中';                    // 单引号是 char，双引号是 String
boolean ok = true;
var list = new java.util.ArrayList<String>();  // var：局部变量类型推断（10 起）
final double PI = 3.14159;        // final = 不能再赋值（≈ C++ const 变量）
int big = 1_000_000;              // 下划线可读性
```

**包装类与装箱**（C++ 没有的东西，必须懂）：

```java
Integer boxed = 127;              // 自动装箱 int -> Integer
int raw = boxed;                  // 自动拆箱
System.out.println(boxed == 127); // true  （缓存 -128~127）
System.out.println(new Integer(1000) == new Integer(1000)); // false ← 比的是引用！
```

**规则：基本类型用 `==`，对象（String/Integer/自己写的类）用 `equals`。**

类型转换：

```java
double d = 3;                     // 隐式：int -> double
int i = (int) 3.99;               // 显式强转，截断 = 3
int n = Integer.parseInt("42");   // String -> int
double x = Double.parseDouble("3.14");
String s = String.valueOf(42);    // 任意 -> String
```

---

## §3 字符串（本项目高频）

```java
String s = "1+2*3";
int len = s.length();             // 注意是方法 length()，数组才是属性 length
char c = s.charAt(0);             // '1'
boolean has = s.indexOf('+') >= 0;
String sub = s.substring(1, 3);   // [1,3) → "+2"
String t = s.strip();             // 去首尾空白（trim 是旧 API）
String low = s.toLowerCase();
```

**拼接**：少量用 `+`，循环里用 `StringBuilder`：

```java
StringBuilder sb = new StringBuilder();
for (String tok : tokens) sb.append(tok).append(' ');
String result = sb.toString().strip();
```

**比较必须用 `equals`**：

```java
String a = "x", b = "x";
a == b            // 可能 true 也可能 false（比引用），永远别用
a.equals(b)       // true  ✅
"x".equals(a)     // 也推荐这种写法，a 为 null 时不会 NPE
```

**格式化**：

```java
String.format("%.2f", 3.14159)   // "3.14"
String.format("%.10g", 0.1 + 0.2) // "0.3"（去尾零的常用手段）
```

---

## §4 数组与集合

**数组**（长度固定）：

```java
int[] a = new int[3];
double[] xs = {1.0, 2.0};
a.length          // 属性，没有括号
Arrays.toString(xs)   // "[1.0, 2.0]"，直接 println 数组只会打印地址
Arrays.sort(xs);
```

**List（≈ vector）**——注意泛型不能是基本类型：

```java
List<Integer> nums = new ArrayList<>();   // 不能写 List<int>
nums.add(3);
int first = nums.get(0);
int n = nums.size();                      // 方法 size()
for (int v : nums) { }                    // 增强 for
```

**Map（≈ unordered_map）**：

```java
Map<String, Integer> m = new HashMap<>();
m.put("a", 1);
int v = m.getOrDefault("b", 0);
for (var e : m.entrySet()) { }            // e.getKey() / e.getValue()
```

**Deque（≈ 栈，本项目求值用它）**：

```java
Deque<Double> stack = new ArrayDeque<>();
stack.push(1.0);      // 压栈（等价 addFirst）
double top = stack.pop();   // 弹栈（等价 removeFirst），空栈抛异常
double peek = stack.peek(); // 只看不弹
```

**不可变集合**（测试数据常用）：

```java
List<String> ops = List.of("+", "-", "*", "/");
```

---

## §5 控制流

```java
if (x > 0) { } else if (x == 0) { } else { }

for (int i = 0; i < n; i++) { }
for (Token t : tokens) { }          // 增强 for
while (stack.size() > 1) { }
do { } while (cond);

// 新式 switch（JDK 14+，本项目推荐）
String name = switch (type) {
    case NUM -> "数字";
    case PLUS, MINUS -> "加减";
    default -> "其他";
};
```

- `&&`/`||` 短路，与 C++ 相同
- 三目 `cond ? a : b` 相同
- `break` 跳出循环；带标签 `outer:` 可以使用但少用

---

## §6 方法与参数

```java
public static int add(int a, int b) { return a + b; }

// 只有"值传递"：传对象传的是引用的副本
public static void fill(List<Integer> list) {
    list.add(1);        // 影响调用方（同一对象）
    list = new ArrayList<>();  // 只改本地引用，不影响调用方
}

// 没有默认参数！用重载代替
public static String format(double v) { return format(v, 2); }
public static String format(double v, int digits) { return String.format("%." + digits + "f", v); }

// 可变参数 ≈ C++ 的 ...
public static void log(String... parts) { }
```

命名：方法/变量 `camelCase`，常量 `UPPER_SNAKE`，类 `PascalCase`，包全小写。

---

## §7 类、封装、构造器

```java
public class Point {
    private final int x;     // 字段：private + final = 不可变
    private final int y;

    public Point(int x, int y) {   // 构造器：名字与类名同，无返回类型
        this.x = x;                // this 不能省（参数与字段同名）
        this.y = y;
    }

    public int x() { return x; }   // getter（record 可自动生成，见 §9）
    public int sum() { return x + y; }

    @Override
    public String toString() { return "(" + x + ", " + y + ")"; }
}
```

访问修饰符：

| 修饰符 | 可见范围 |
| --- | --- |
| `public` | 任何地方 |
| `protected` | 本类 + 子类 + 同包 |
| （默认，不写） | 同包 |
| `private` | 仅本类 |

---

## §8 继承、接口、多态

```java
public abstract class Shape {
    public abstract double area();      // 抽象方法：无方法体
    public String describe() { return "面积=" + area(); }
}

public interface Named {
    String name();                      // 接口方法默认 public abstract
    default String tag() { return "[" + name() + "]"; }  // default 可给实现
}

public class Circle extends Shape implements Named {   // 单继承 + 多接口
    private final double r;
    public Circle(double r) { this.r = r; }
    @Override public double area() { return Math.PI * r * r; }
    @Override public String name() { return "圆"; }
}

// 多态：父类型引用指向子类对象，调用动态分派
Shape s = new Circle(1.0);
System.out.println(s.describe());       // 面积=3.14159...
```

> **本项目的"一核两壳"正是这个机制**：`RpnService` 是核心，`WebApi` 与 `SwingShell` 是两个调用方；将来若加第三种界面，核心一行不改。

---

## §9 record 与 enum（本项目必用）

### record：一行定义一个不可变值对象

```java
public record Token(TokenType type, String text, int pos, double value) { }
```

编译器自动生成：全参构造器、`type()`/`text()`/`pos()`/`value()` 访问器（不是 getXxx）、`equals`、`hashCode`、`toString`。字段全 `final`。

需要校验时用**紧凑构造器**：

```java
public record Token(TokenType type, String text, int pos, double value) {
    public Token {
        if (pos < 0) throw new IllegalArgumentException("pos 不能为负: " + pos);
        text = text == null ? "" : text;   // 可对参数重新赋值（会写回字段）
    }
}
```

### enum：本质是类

```java
public enum TokenType {
    NUM, PLUS, MINUS, STAR, SLASH, PERCENT, LPAREN, RPAREN, EOF
}

// 可以带字段与方法
public enum ErrKind {
    LEX("词法错误"), SYNTAX("语法错误"), RUNTIME("运行时错误");
    private final String label;
    ErrKind(String label) { this.label = label; }
    public String label() { return label; }
}
```

`switch` 对 enum 用**不带类名前缀**的常量名（`case NUM ->`）。

---

## §10 异常

层次：`Throwable` → `Error` / `Exception` → `RuntimeException`。

- **checked**（继承 `Exception`）：必须 `try/catch` 或 `throws` 声明，编译器强制
- **unchecked**（继承 `RuntimeException`）：编译器不管，随时可抛

本项目的统一错误用 unchecked：

```java
public class CompileException extends RuntimeException {
    public enum Kind { LEX, SYNTAX, RUNTIME }

    private final Kind kind;
    private final int pos;

    public CompileException(Kind kind, int pos, String message) {
        super("[" + kind + "错误] 第 " + (pos + 1) + " 个字符：" + message);
        this.kind = kind;
        this.pos = pos;
    }

    public Kind kind() { return kind; }
    public int pos() { return pos; }
}
```

```java
try {
    double v = evaluator.eval(rpn);
} catch (CompileException e) {
    System.out.println(e.getMessage());   // 直接给用户看
}
```

**注意**：`pos` 内部用 0 基，消息里加 1 显示——这个转换只在一个地方做（构造器里），别散在各处。

---

## §11 泛型（够用即可）

```java
List<Token> tokens = new ArrayList<>();
Map<TokenType, Integer> counter = new HashMap<>();
public static <T> void printAll(List<T> list) { }
// 通配符（了解即可）：List<? extends Number>
```

---

## §12 常用标准库速查（本项目会用）

| 需求 | 写法 |
| --- | --- |
| 字符串转数字 | `Double.parseDouble(s)` / `Integer.parseInt(s)` |
| 判字符类型 | `Character.isDigit(c)` / `Character.isWhitespace(c)` |
| 判空白 | `c == ' ' \|\| c == '\t'`（本项目只支持空格即可） |
| 取整/绝对值 | `Math.round(x)` / `Math.abs(x)` |
| 格式化小数 | `String.format("%.10g", x)` |
| 非空校验 | `Objects.requireNonNull(x, "x 不能为 null")` |
| 系统属性 | `System.getProperty("java.version")` |
| 计时 | `System.nanoTime()` 差值 / 1e6 = 毫秒 |
| 输出到字符串 | `StringBuilder` + `toString()` |

---

## §13 代码风格（我会按这个批，业界标准）

- 命名：类 `PascalCase`、方法/变量 `camelCase`、常量 `UPPER_SNAKE`、包全小写
- 缩进 4 空格；行宽 ≤100；大括号 K&R（`{` 不换行）
- **public 类/方法必须有 Javadoc**：`/** 一句话说清做什么。 @param ... @return ... @throws ... */`
- 注释解释 **为什么**，不解释 "i++ 是自增"
- `import` 写具体的类，不用 `import java.util.*`
- 不用魔法数字：`if (pos < 0)` 取代 `if (pos < 0 - 0)`

---

## §14 练习路线（今晚做 1–2，明晚做 3–4）

### 练习 1（10 分钟）跑通工具链
写 `src/rpn/Practice1.java`：打印 `args.length` 和每个参数，然后 `java -cp out\classes rpn.Practice1 a b` 应输出 2 / a / b。

### 练习 2（20 分钟）类型与字符串
`Practice2.java` 里打印这些，**先猜结果再运行**：

```java
System.out.println(1 / 3);
System.out.println(1.0 / 3);
System.out.println(7 % 3 + " " + (-7 % 3) + " " + (7 % -3));
String a = "abc"; String b = new String("abc");
System.out.println(a == b);           // ?
System.out.println(a.equals(b));      // ?
System.out.println("x=" + 1 + 2);     // ?
System.out.println(1 + 2 + "=x");     // ?
```

<details><summary>预期输出</summary>

```
0
0.3333333333333333
1 -1 1
false
true
x=12
3=x
```
</details>

### 练习 3（20 分钟）集合与栈
`Practice3.java`：用 `List<Integer>` 存 1..5 求和并打印；用 `Deque<Integer>` 把 1..5 逆序打印成 `5 4 3 2 1`；用 `Map<String,Integer>` 统计 `"a","b","a"` 出现次数。

### 练习 4（30 分钟，明晚）类 + record + 接口 + 异常
定义 `interface Named { String name(); }`、`record Circle(double r) implements Named`（面积 = πr²）、`class Triangle`（底高），找出面积最大者；再写一个 `CompileException` 并在 `r < 0` 时抛出，打印其 `getMessage()`。

---

## §15 常见报错翻译表

| javac 报错 | 真实原因 |
| --- | --- |
| 方法声明无效; 需要返回类型 | 忘写 `void`/返回类型（C++ 习惯） |
| 类 X 是公共的, 应在名为 X.java 的文件中声明 | 文件名与 public 类名不一致（含大小写） |
| 找不到符号 | 名字拼错、变量作用域外、忘 `import` |
| 可能尚未初始化变量 | 局部变量声明后没赋值就用 |
| 不兼容的类型 | 类型不匹配（`int` 与 `String` 相加时注意顺序） |
| 需要的 ';' | 上一行少了分号 |
| 无法将类 X 中的方法应用到给定类型 | 参数个数/类型不对（没有默认参数！） |
| 已在 X 中定义 | 重复声明或导入了两个同名类 |

运行时常见：
- `NullPointerException`：引用是 `null` 就调用方法 → 先判 `null`
- `ArrayIndexOutOfBoundsException`：下标越界 → 检查 `<=` 与 `<`
- `NumberFormatException`：`parseDouble` 收到非数字串
