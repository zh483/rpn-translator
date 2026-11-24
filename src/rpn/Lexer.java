package rpn;
import java.util.ArrayList;
import java.util.List;
/**
 * 词法分析器
 * Lexer
 */
public class Lexer {
    /**
     * 扫描整个输入串 返回记号序列
     * @param src 表达式原文
     * @return 返回token流
     * @throws CompileException 输出词法分析错误+词法错误位置
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
            else if((c>='0' && c<='9') || c=='.'){
                int start=i;
                boolean havepot=false;
                while ((c>='0' && c<='9') || (c=='.' && !havepot)) {
                    if(c=='.') havepot=true;
                    ++i;
                    if(i==src.length()) break;
                    c=src.charAt(i);
                }
                String NUM=src.substring(start,i);
                if(NUM.length()==1 && NUM.charAt(0)=='.')  //单独一个点
                    throw new CompileException(rpn.CompileException.Kind.LEX,
                                                start, "非法字符: '"+NUM+"'");
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
                        throw new CompileException(rpn.CompileException.Kind.LEX,
                                                     i, "非法字符: '"+c+"'");
                }
                ++i;
            }
        }
        tokens.add(new Token(TokenType.EOF, "", src.length(), 0));
        return tokens;
    }
}
