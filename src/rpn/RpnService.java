package rpn;

/**
 * 整个计算结构的门面 
 * <p><evaluate 输入要计算的式子 返回计算结果 并正确抛出异常>
 */
public class RpnService {
    /**
     * 一次调用完成：词法分析 → 语法分析（生成后缀序列）→ 求值 → 格式化。
     *
     * @param expression 中缀表达式
     * @return 结果快照（含原文、后缀文本、结果文本）
     * @throws CompileException 词法/语法/运行时错误
     */
    public RpnResult evaluate(String expression) { 
            Lexer lexer=new Lexer();
            var tokens=lexer.scan(expression);
            Parser parser=new Parser(tokens);
            var rpn=parser.parse();
            StringBuilder sBuilder=new StringBuilder();
            for(var token:rpn){
                sBuilder.append(token.text());
                sBuilder.append(' ');
            }
            String rpnText=sBuilder.toString().strip();
            Evaluator evaluator=new Evaluator();
            double eval=evaluator.eval(rpn);
            return new RpnResult(expression, rpnText, ResultFormatter.format(eval));
    }
    public record RpnResult(String expression,String rpnText, String valueText) {}
}
