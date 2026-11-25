package rpn;

import java.math.BigDecimal;
import java.math.MathContext;
/**
 * 把double的结果转换成string
 * <p><format 输入计算结果 返回对应的string>
 */
public class ResultFormatter {
    public static String format(double value){
        if(!Double.isFinite(value)){
           return String.valueOf(value);
        }
        double x=(value==0)?0.0:value;
        if(Math.abs(x-Math.rint(x))<1e-9) return String.format("%.0f", x);
        return BigDecimal.valueOf(x).
                        round(new MathContext(10)).
                        stripTrailingZeros().
                        toPlainString();
      
    }
}

