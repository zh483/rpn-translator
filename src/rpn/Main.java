package rpn;

import javax.swing.SwingUtilities;
import javax.swing.UIManager;
import java.awt.Font;
/**
 * 主程序入口
 * <p><>
 */
public class Main {
    public static void main(String[] args) {
        try { UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName()); }
        catch (Exception ignored) { }
        UIManager.put("Label.font", new Font("Microsoft YaHei", Font.PLAIN, 14));
        UIManager.put("Button.font", new Font("Microsoft YaHei", Font.PLAIN, 14));
        UIManager.put("TextField.font", new Font("Microsoft YaHei", Font.PLAIN, 16));
        UIManager.put("TextArea.font", new Font("Microsoft YaHei", Font.PLAIN, 14));
        SwingUtilities.invokeLater(() -> new SwingShell().setVisible(true));

    }
}