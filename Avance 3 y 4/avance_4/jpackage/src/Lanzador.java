import java.awt.Desktop;
import java.io.File;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.nio.file.Paths;
import javax.swing.JOptionPane;

/** Lanzador del dashboard climatico: inicia app.py y abre el navegador. */
public class Lanzador {
    public static void main(String[] args) throws Exception {
        Path raiz = ubicarRaiz();
        String python = System.getProperty("os.name").toLowerCase().contains("win") ? "python" : "python3";
        ProcessBuilder pb = new ProcessBuilder(python, "app.py", "8501", "--no-abrir");
        pb.directory(raiz.toFile()).inheritIO();
        Process proceso;
        try {
            proceso = pb.start();
        } catch (Exception e) {
            JOptionPane.showMessageDialog(null, "No se encontro Python 3 con pandas y matplotlib.\n"
                + "Instale las dependencias con: pip install -r requirements.txt", "Dashboard climatico", JOptionPane.ERROR_MESSAGE);
            return;
        }
        Runtime.getRuntime().addShutdownHook(new Thread(proceso::destroy));
        Thread.sleep(2500);
        if (Desktop.isDesktopSupported()) Desktop.getDesktop().browse(new URI("http://127.0.0.1:8501"));
        JOptionPane.showMessageDialog(null, "Dashboard en http://127.0.0.1:8501\nCierre esta ventana para detenerlo.", "Dashboard climatico", JOptionPane.INFORMATION_MESSAGE);
        proceso.destroy();
    }

    /** Busca la carpeta que contiene app.py (junto a la app instalada o en el proyecto). */
    static Path ubicarRaiz() throws URISyntaxException {
        Path jar = Paths.get(Lanzador.class.getProtectionDomain().getCodeSource().getLocation().toURI()).toAbsolutePath();
        Path p = jar.getParent();
        for (int i = 0; i < 6 && p != null; i++, p = p.getParent()) {
            if (new File(p.toFile(), "app.py").exists()) return p;
            File proyecto = new File(p.toFile(), "proyecto");
            if (new File(proyecto, "app.py").exists()) return proyecto.toPath();
        }
        return Paths.get("").toAbsolutePath();
    }
}
