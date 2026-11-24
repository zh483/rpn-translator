package rpn;

import java.util.ArrayList;
import java.util.List;
/**
 * 用递归下降法分析 LL(1) 文法
 * Parser
 */
public class Parser {
    private final List<Token>tokens;
    private int pos;
    Parser(List<Token>tokens){
        this.tokens=tokens;
        this.pos=0;
    }

    public List<Token> parse(){
        var result=expr();
        expect(TokenType.EOF);
        return result;
    }

    private List<Token> expr(){
        if(check(TokenType.NUM) ||check(TokenType.MINUS) ||check(TokenType.LPAREN)){
            List<Token> result=new ArrayList<>();
            result.addAll(term());
            var right=exprPrime();
            if(right!=null)
                result.addAll(right);
            return result;
        }
        throw new CompileException(CompileException.Kind.SYNTAX,
                                        tokens.get(pos).pos(),
                                        "期望读到 数字 负号 左括号 实际读到: "+
                                        tokens.get(pos).type().label());
    }
    private List<Token> exprPrime(){
        if(check(TokenType.PLUS) || check(TokenType.MINUS)){
            var token=next();
            List<Token> result=new ArrayList<>();
            var left=term();
            if(left!=null)
                result.addAll(left);
            result.add(token);
            var right=exprPrime();
            if(right!=null)
                result.addAll(right);
            return result;
        }
        else if(check(TokenType.RPAREN) || check(TokenType.EOF)){
            return List.of();
        }
        throw new CompileException(CompileException.Kind.SYNTAX,
                                        tokens.get(pos).pos(),
                                        "期望读到 加号 减号 右括号 终止符 实际读到: "+
                                        tokens.get(pos).type().label());
    }
    private List<Token> term(){
        if(check(TokenType.NUM) || check(TokenType.MINUS) || check(TokenType.LPAREN)){
            List<Token> result=new ArrayList<>();
            result.addAll(factor());
            var right=termPrime();
            if(right!=null)
                result.addAll(right);
            return  result;
        }
        throw new CompileException(CompileException.Kind.SYNTAX,
                                        tokens.get(pos).pos(),
                                        "期望读到 数字 减号 左括号 实际读到: "+
                                        tokens.get(pos).type().label());
    }
    private List<Token> termPrime(){
        if(check(TokenType.STAR) || check(TokenType.SLASH) || check(TokenType.PERCENT)){
            var token=next();
            List<Token> result=new ArrayList<>();
            var left=factor();
            if(left!=null)
                result.addAll(left);
            result.add(token);
            var right=termPrime();
            if(right!=null)
                result.addAll(right);
            return result;
        }
        else if(check(TokenType.PLUS) || check(TokenType.MINUS) || 
                check(TokenType.EOF) || check(TokenType.RPAREN))
        {
            return List.of();
        }
        throw new CompileException(CompileException.Kind.SYNTAX,
                                        tokens.get(pos).pos(),
                                        "期望读到 加号 减号 乘号 除号 取模 左括号 终止符 实际读到: "+
                                        tokens.get(pos).type().label());
    }
    private List<Token> factor(){
        if(check(TokenType.NUM)){
            var token=next();
            List<Token> result=new ArrayList<>();
            result.add(token);
            return result;
        }
        else if(check(TokenType.MINUS)){
            var token=next();
            List<Token> result=new ArrayList<>();
            result.addAll(factor());
            result.add(new Token(TokenType.NEG,"neg", token.pos(),token.value()));
            return result;
        }
        else if(check(TokenType.LPAREN)){
            next();
            List<Token> result=new ArrayList<>();
            result.addAll(expr());
            expect(TokenType.RPAREN);
            return result;
        }
        throw new CompileException(CompileException.Kind.SYNTAX,
                                        tokens.get(pos).pos(),
                                        "期望读到 数字 负号 左括号 终止符 实际读到: "+
                                        tokens.get(pos).type().label());
    }
    private boolean check(TokenType type){
        return tokens.get(pos).type()==type;
    }
    private Token next(){
        return tokens.get(pos++);
    }
    private Token expect(TokenType type){
        if(!check(type)) throw new CompileException(CompileException.Kind.SYNTAX,
                                                tokens.get(pos).pos(),
                                                "期望读到: "+type.label()+ " 实际读到: "+
                                                tokens.get(pos).type().label());
        return next();
    }
}
