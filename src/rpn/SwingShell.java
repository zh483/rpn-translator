package rpn;

import javax.swing.BorderFactory;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;

import java.awt.BorderLayout;
import java.awt.FlowLayout;
import java.awt.GridLayout;
import java.awt.Color;
import java.awt.Font;
import java.awt.Dimension;

/**
 * 主要的窗口
 * <p><>
 */
public class SwingShell extends JFrame {
    private final JTextField inputField = new JTextField(24);
    private final JButton calcButton = new JButton("翻译并求值");
    private final JButton clearButton = new JButton("清空");
    private final JTextArea infixArea=new JTextArea();
    private final JTextArea rpnArea=new JTextArea();
    private final JTextArea valueArea=new JTextArea();
    private final JLabel errorLabel = new JLabel("就绪");
    private final RpnService service=new RpnService();
    SwingShell(){
        super();
        
        calcButton.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
        clearButton.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
        errorLabel.setFont(new Font("Microsoft YaHei", Font.PLAIN, 14));
     
        Dimension d = new Dimension(120, 32);
        calcButton.setPreferredSize(d);
        clearButton.setPreferredSize(d);

        this.setTitle("算术表达式翻译与求值系统");
        this.setSize(720, 230);
        this.setMinimumSize(new Dimension(720, 230));
        this.setResizable(false);  
        this.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        this.setLayout(new BorderLayout());
        
        JPanel top = new JPanel(new FlowLayout(FlowLayout.LEFT));
        top.add(new JLabel("表达式："));
        top.add(inputField);        // JTextField，setColumns(20)
        top.add(calcButton);        
        top.add(clearButton);      
        this.add(top, BorderLayout.NORTH);
        JPanel center = new JPanel(new GridLayout(1, 3, 12, 12));   // 1 行 3 列，间距 12
        center.add(makePanel("中缀表达式", infixArea));
        center.add(makePanel("逆波兰式",  rpnArea));
        center.add(makePanel("计算结果",  valueArea));
        this.add(center, BorderLayout.CENTER);
        errorLabel.setForeground(Color.GRAY);
        this.add(errorLabel, BorderLayout.SOUTH);
        calcButton.addActionListener(e->{
            String expr=inputField.getText()==null?"":inputField.getText().strip();
            try {
                long t0 = System.nanoTime();
                var result=service.evaluate(expr);
                long us = (System.nanoTime() - t0) / 1000;
                infixArea.setText(result.expression());
                rpnArea.setText(result.rpnText());
                valueArea.setText(result.valueText());
                errorLabel.setText("就绪 · 耗时 " + us + " μs");
                errorLabel.setForeground(Color.GRAY);
            } catch (CompileException er) {
                errorLabel.setText(er.getMessage());
                errorLabel.setForeground(Color.RED);
                infixArea.setText(expr);
                rpnArea.setText("-");
                valueArea.setText("-");
            }
        });
        clearButton.addActionListener(e->{
            inputField.setText("");
            infixArea.setText("");
            rpnArea.setText("");
            valueArea.setText("");
            errorLabel.setText("就绪");
            errorLabel.setForeground(Color.GRAY);
        });
        inputField.addActionListener(e -> calcButton.doClick());
        this.setLocationRelativeTo(null);
        
    }
    private JPanel makePanel(String title, JTextArea Area) {
        Area.setEditable(false);
        JPanel p=new JPanel(new BorderLayout());
        p.add(new JLabel(title),BorderLayout.NORTH);
        p.add(new JScrollPane(Area),BorderLayout.CENTER);
        p.setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        return p;
    }
    
}
