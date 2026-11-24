package rpn;
/**
 * 词法单元类型
 * TokenType
 */
public enum TokenType{
    NUM("数字"),
    PLUS("加号"),
    MINUS("减号"),
    NEG("负号"),
    STAR("乘号"),
    SLASH("除号"),
    PERCENT("取模"),
    LPAREN("左括号"),
    RPAREN("右括号"),
    EOF("结束符号");
    private final String label;
    TokenType(String message){
        this.label=message;
    }
    public String label(){
        return label;
    }
}
