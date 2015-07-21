import java.io.*;
import java.util.*;
import ij.IJ;
import ij.ImagePlus;
import ij.io.*;
import ij.plugin.PlugIn;
import javax.swing.JFileChooser;

public class Open_Images_In_Folder implements PlugIn {	
	@Override
	public void run(String arg) {
		JFileChooser dialog = new JFileChooser();
		dialog.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
		dialog.showOpenDialog(null);
		if (dialog.getSelectedFile() == null)
			return; // canceled
		File startdir = dialog.getSelectedFile();
		Vector<ImagePlus> imps = new Vector<ImagePlus>();
		FileFilter filter = new FileFilter() {
    		public boolean accept(File file) {
				if (file.isFile() && file.getName().contains(".dm3")) return true;
				return false;
			}
		};
		for ( File file : startdir.listFiles(filter)) {
			Opener opener = new Opener();
			imps.add(opener.openImage(file.getPath()));
		}
		for ( ImagePlus imp : imps ) {
			imp.show();		
		}
	}
}