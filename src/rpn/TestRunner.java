package rpn;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
/**
 * 内部测试程序,目前显示词法分析器的结果
 * TestRunner
 */
public class TestRunner {
    private static int pass = 0;
    private static int fail = 0;
    private static final Path CASES = Path.of("testdata", "testcases.txt");
    public static void main(String[] args){
        List<String> lines;
        try {
            lines = Files.readAllLines(CASES, StandardCharsets.UTF_8);
        } catch (IOException e) {
            System.out.println("读不到 testdata/testcases.txt，请在项目根目录运行"); return;
        }
        for (String raw : lines) {
            String line = raw.strip();
            if (line.isEmpty() || line.startsWith("#")) continue;
            String[] f = line.split("\\|", -1);        // -1：保留末尾空列
            String id = f[0].strip(), src = f[1].strip();
            String kind = f[2].strip(), expect = f[3].strip();
            if (kind.equals("OK"))  
                expectTokens(id, src, expect);
            else 
                expectError(id, src, Integer.parseInt(expect));

        }
        report(null, null, null, null, true);
    }

    /** 把 token 流渲染成稳定格式：TYPE(text)@pos，用空格分隔。 */
    private static String render(List<Token> tokens) { 
        StringBuilder stb=new StringBuilder();
        for(var token:tokens){
            switch (token.type()) {
                case NUM:
                    stb.append("NUM(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case PLUS:
                    stb.append("PLUS(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case MINUS:
                    stb.append("MINUS(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case STAR:
                    stb.append("STAR(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case SLASH:
                    stb.append("SLASH(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case PERCENT:
                    stb.append("PERCENT(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case LPAREN:
                    stb.append("LPAREN(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case RPAREN:
                    stb.append("RPAREN(");
                    stb.append(token.text());
                    stb.append(")@");
                    stb.append(token.pos());
                    stb.append(' ');
                    break;
                case EOF:
                    stb.append("EOF");
                    stb.append('@');
                    stb.append(token.pos());
                    break;
                default:
                    break;
            }
        }
        String result=stb.toString();
        return result;
    }

    /** 断言：跑一遍，把实际渲染结果和期望比。 */
    private static void expectTokens(String id, String src, String expected) { 
        Lexer lex=new Lexer();
        String actual=render(lex.scan(src));
        report(id, src, expected, actual,false);
    }

    /** 断言：必须抛词法错误，且位置（1 基）正确。 */
    private static void expectError(String id, String src, int pos1Based) { 
        String actual="-1";
        Lexer lex=new Lexer();
        try {
            lex.scan(src);
        } catch (CompileException e) {
            actual=String.valueOf(e.pos());
        }
        report(id, src, String.valueOf(pos1Based),actual, false);
    }

    /** 统一打印一行结果，维护 pass/fail 计数。 */
    private static void report(String id, String src, String expected, String actual, boolean ok) { 
        if(ok){
            System.out.print("总共 "+pass+fail+" 次 失败 "+fail+"次 成功 "+pass+" 次");
        }
        else{
            System.out.println(id+' '+src+" 期望="+expected+" 实际="+actual+(expected.equals(actual)?" PASS":" FAIL"));
            if(expected.equals(actual)) ++pass;
            else ++fail;
        }
    }
}
