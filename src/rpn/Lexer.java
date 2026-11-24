package rpn;
import java.util.ArrayList;
import java.util.List;

/**
 * 词法分析器：把表达式字符串切分为记号序列。
 *
 * <p>支持的记号：整数与浮点常量（如 {@code 12}、{@code 3.14}、{@code .5}、{@code 5.}）、
 * 运算符 {@code + - * / %}、括号 {@code ( )}，以及末尾的 EOF。
 * 遇到非法字符或非法数字时抛出 {@link CompileException}（类别 LEX，携带 0 基字符位置）。
 */
public class Lexer {

    /**
     * 扫描整个输入串，返回记号序列；末尾总追加一个 EOF 记号。
     *
     * @param src 表达式原文
     * @return 记号列表，至少包含一个 EOF
     * @throws CompileException 遇到非法字符时抛出（{@code Kind.LEX}）
     */
    public List<Token> scan(String src){
        List<Token>tokens=new ArrayList<>();
        int i=0;
        while (i<src.length()) {
            char c=src.charAt(i);
            if(Character.isWhitespace(c)) {
                ++i;
                continue;
            }
            else if(Character.isDigit(c) || c=='.'){
                int start=i;
                boolean havepot=false;
                while (Character.isDigit(c) || (c=='.' && !havepot)) {
                    if(c=='.') havepot=true;
                    ++i;
                    if(i==src.length()) break;
                    c=src.charAt(i);
                }
                String NUM=src.substring(start,i);
                if(NUM.length()==1 && NUM.charAt(0)=='.')  //单独一个点
                    throw new CompileException(rpn.CompileException.Kind.LEX, start, "非法字符: '"+NUM+"'");
                tokens.add(new Token(TokenType.NUM,NUM,start, Double.parseDouble(NUM)));
                continue;
            }
            else{
                switch (c) {
                    case '+':
                        tokens.add(new Token(TokenType.PLUS, "+", i, 0));
                        break;
                    case '-':
                        tokens.add(new Token(TokenType.MINUS, "-", i, 0));
                        break;
                    case '*':
                        tokens.add(new Token(TokenType.STAR, "*", i, 0));
                        break;
                    case '/':
                        tokens.add(new Token(TokenType.SLASH, "/", i, 0));
                        break;
                    case '%':
                        tokens.add(new Token(TokenType.PERCENT, "%", i, 0));
                        break;
                    case '(':
                        tokens.add(new Token(TokenType.LPAREN, "(", i, 0));
                        break;
                    case ')':
                        tokens.add(new Token(TokenType.RPAREN, ")", i, 0));
                        break;
                    default:
                        throw new CompileException(rpn.CompileException.Kind.LEX, i, "非法字符: '"+c+"'");
                }
                ++i;
            }
        }
        tokens.add(new Token(TokenType.EOF, "", src.length(), 0));
        return tokens;
    }
}
