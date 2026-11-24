package rpn;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;
/**
 * 
 * 对逆波兰表达式求值
 * 
 * <p><eval接受正确的逆波兰表达式 不检查正确 返回答案
 *  出错:返回CompileException提示计算时期错误>
 */
public class Evaluator {
    /**
     * 对后缀序记号序列求值。
     *
     * @param rpn 后缀序记号序列（由 Parser 产出）
     * @return 计算结果
     * @throws CompileException 运行时错误（除数为零、序列不完整等），带字符位置
     */
    public double eval(List<Token> rpn) { 
        Deque<Double>stak=new ArrayDeque<>();
        for(var token:rpn){
            switch (token.type()) {
                case NUM:
                    stak.push(token.value());
                    break;
                case NEG:
                    stak.push(-stak.pop());
                    break;
                default:
                    double r=stak.pop();
                    double l=stak.pop();
                    switch (token.type()) {
                        case PLUS:
                            stak.push(l+r);
                            break;
                        case MINUS:
                            stak.push(l-r);
                            break;
                        case PERCENT:
                            if(r==0)
                                throw new CompileException(CompileException.Kind.RUNTIME,
                                                            token.pos(),
                                                    "不能对0取模");
                            stak.push(l%r);
                            break;
                        case SLASH:
                            if(r==0)
                                throw new CompileException(CompileException.Kind.RUNTIME,
                                                            token.pos(),
                                                    "不能除0");
                            stak.push(l/r);
                            break;
                        case STAR:
                            stak.push(l*r);
                            break;
                        default:
                            break;
                    }
                    break;
            }
        }
        return stak.pop();
    }
}
