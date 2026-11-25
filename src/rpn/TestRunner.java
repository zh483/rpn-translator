package rpn;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * 批量回归测试入口：依次跑词法、语法、求值、格式化四组用例，输出逐条结果与总计。
 *
 * <p>用例数据放在 {@code testdata/} 下，每行格式为「编号 | 输入 | 类型 | 期望」，
 * 以 {@code #} 开头的行与空行会被跳过。全部通过时退出码为 0，存在失败时为 1，
 * 因此可以被脚本或 CI 直接调用。
 *
 * <p>用法：在项目根目录执行 {@code java -cp out/classes rpn.TestRunner}。
 */
public class TestRunner {

    private static final Path LEX_CASES = Path.of("testdata", "testcases.txt");
    private static final Path PARSE_CASES = Path.of("testdata", "parsecases.txt");
    private static final Path EVAL_CASES = Path.of("testdata", "evalcases.txt");
    private static final Path FORMAT_CASES = Path.of("testdata", "formatcases.txt");

    private static int pass = 0;
    private static int fail = 0;

    /**
     * 跑完四组用例并打印汇总。
     *
     * @param args 未使用
     */
    public static void main(String[] args) {
        try {
            runLexerCases();
            runParseCases();
            runEvalCases();
            runFormatCases();
        } catch (IOException e) {
            System.out.println("读不到用例文件，请在项目根目录运行：" + e.getMessage());
            System.exit(2);
        }
        System.out.printf("%n合计：通过 %d / 失败 %d%n", pass, fail);
        if (fail > 0) {
            System.exit(1);
        }
    }

    // ---------------------------------------------------------------- 三组用例

    /** 词法组：OK 比对记号流文本，ERR 比对词法错误位置（0 基）。 */
    private static void runLexerCases() throws IOException {
        System.out.println("== 词法分析 ==");
        for (String[] f : readCases(LEX_CASES)) {
            String id = f[0], src = f[1], kind = f[2], expect = f[3];
            String actual;
            boolean ok;
            try {
                actual = renderTokens(new Lexer().scan(src));
                ok = kind.equals("OK") && actual.equals(expect);
            } catch (CompileException e) {
                actual = describe(e);
                ok = kind.equals("ERR")
                        && e.kind() == CompileException.Kind.LEX
                        && String.valueOf(e.pos()).equals(expect);
            }
            record(id, src, expect, actual, ok);
        }
    }

    /** 语法组：POK 比对后缀序列文本，PERR 比对语法错误位置（0 基）。 */
    private static void runParseCases() throws IOException {
        System.out.println("== 语法分析 ==");
        for (String[] f : readCases(PARSE_CASES)) {
            String id = f[0], src = f[1], kind = f[2], expect = f[3];
            String actual;
            boolean ok;
            try {
                actual = renderRpn(new Parser(new Lexer().scan(src)).parse());
                ok = kind.equals("POK") && actual.equals(expect);
            } catch (CompileException e) {
                actual = describe(e);
                ok = kind.equals("PERR")
                        && e.kind() == CompileException.Kind.SYNTAX
                        && String.valueOf(e.pos()).equals(expect);
            }
            record(id, src, expect, actual, ok);
        }
    }

    /** 求值组：VOK 用容差比较数值，VERR 比对运行时错误位置（0 基）。 */
    private static void runEvalCases() throws IOException {
        System.out.println("== 求值 ==");
        for (String[] f : readCases(EVAL_CASES)) {
            String id = f[0], src = f[1], kind = f[2], expect = f[3];
            String actual;
            boolean ok;
            try {
                List<Token> rpn = new Parser(new Lexer().scan(src)).parse();
                double value = new Evaluator().eval(rpn);
                actual = String.valueOf(value);
                ok = kind.equals("VOK") && Math.abs(value - Double.parseDouble(expect)) < 1e-9;
            } catch (CompileException e) {
                actual = describe(e);
                ok = kind.equals("VERR")
                        && e.kind() == CompileException.Kind.RUNTIME
                        && String.valueOf(e.pos()).equals(expect);
            }
            record(id, src, expect, actual, ok);
        }
    }

    /** 格式化组（全链路）：FOK 比对界面显示文本，FERR 比对错误位置（0 基）。 */
    private static void runFormatCases() throws IOException {
        System.out.println("== 格式化（RpnService）==");
        RpnService service = new RpnService();
        for (String[] f : readCases(FORMAT_CASES)) {
            String id = f[0], src = f[1], kind = f[2], expect = f[3];
            String actual;
            boolean ok;
            try {
                RpnService.RpnResult result = service.evaluate(src);
                actual = result.valueText();
                ok = kind.equals("FOK") && actual.equals(expect);
            } catch (CompileException e) {
                actual = describe(e);
                ok = kind.equals("FERR") && String.valueOf(e.pos()).equals(expect);
            }
            record(id, src, expect, actual, ok);
        }
    }

    // ---------------------------------------------------------------- 工具方法

    /** 读取用例文件，返回 [编号, 输入, 类型, 期望] 四元组列表。 */
    private static List<String[]> readCases(Path path) throws IOException {
        List<String[]> cases = new ArrayList<>();
        for (String raw : Files.readAllLines(path, StandardCharsets.UTF_8)) {
            String line = raw.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            String[] cells = line.split("\\|", -1);
            for (int i = 0; i < cells.length; i++) {
                cells[i] = cells[i].strip();
            }
            if (cells.length < 4) {
                System.out.println("[WARN] 用例格式不正确，已跳过: " + line);
                continue;
            }
            cases.add(cells);
        }
        return cases;
    }

    /** 词法记号流渲染：TYPE(text)@pos，EOF 无原文只写 EOF@pos。 */
    private static String renderTokens(List<Token> tokens) {
        StringBuilder sb = new StringBuilder();
        for (Token t : tokens) {
            sb.append(t.type());
            if (!t.text().isEmpty()) {
                sb.append('(').append(t.text()).append(')');
            }
            sb.append('@').append(t.pos()).append(' ');
        }
        return sb.toString().strip();
    }

    /** 后缀序列渲染：把记号原文用空格连接，供 POK 断言与人工阅读。 */
    private static String renderRpn(List<Token> rpn) {
        StringBuilder sb = new StringBuilder();
        for (Token t : rpn) {
            sb.append(t.text()).append(' ');
        }
        return sb.toString().strip();
    }

    /** 把异常压成一行可读描述。 */
    private static String describe(CompileException e) {
        return e.kind() + "(pos=" + e.pos() + ") " + e.getMessage();
    }

    /** 记录一条结果并打印。 */
    private static void record(String id, String src, String expect, String actual, boolean ok) {
        if (ok) {
            pass++;
        } else {
            fail++;
        }
        System.out.printf("%-4s %-14s %-5s 期望=%-30s 实际=%s%n",
                id, src, ok ? "PASS" : "FAIL", expect, actual);
    }
}
