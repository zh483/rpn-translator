package rpn;
/**
 * zh483 26/11/24
 * 基础词法单元
 * Token
 * @param type
 * @param text
 * @param pos
 * @param value
 */
public record Token(TokenType type,String text,int pos,double value) {
    public Token{
        if (pos<0) throw new IllegalArgumentException("pos 不能为负数: "+pos);
        text=text==null?"":text;
    }
}
