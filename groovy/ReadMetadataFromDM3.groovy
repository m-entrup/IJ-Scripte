/*
 * @ImagePlus imp
 */

import ij.IJ

prop = imp.getProperties()
IJ.log(prop.Info)
println imp
def count = 0
prop.Info.eachLine {
	def res = it.find(/(?<=Exposure = )(\d+(?:\.\d+)?)/);
	if (res) {
		println it;
		println res;
		count++ 
	}
}
println count
