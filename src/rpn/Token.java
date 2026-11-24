package rpn;
/**
 * 基础词法单元
 * Token
 * @param type 类型
 * @param text 原文
 * @param pos 位置
 * @param value 值
 */
public record Token(TokenType type,String text,int pos,double value) {
    public Token{
        if (pos<0) throw new IllegalArgumentException("pos 不能为负数: "+pos);
        text=text==null?"":text;
    }
}
