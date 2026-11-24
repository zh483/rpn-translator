package rpn;
/**
 * zh483 26/11/24
 * 自定义编译器错误
 * CompileException
*/
public class CompileException extends RuntimeException {
    public enum Kind {
        LEX("词法错误"),SYNTAX("语法错误"),RUNTIME("运行时错误");
        private final String label;
        Kind(String message){
            this.label=message;
        }
        public String label(){
            return  label;
        }
    }
    private final Kind kind;
    private final int pos;
    public CompileException(Kind kind,int pos,String message){
        super("["+kind.label()+"] "+"第 "+(pos+1)+" 个字符: "+message);
        this.kind=kind;
        this.pos=pos;
    }
    public Kind kind(){return kind;};
    public int pos(){return  pos;};
}
