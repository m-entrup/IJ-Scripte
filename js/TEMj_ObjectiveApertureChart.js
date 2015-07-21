/*
 * @Double(label="Voltage in keV",value=200) U_kV
 * @Double(label="focal length in mm",value=1.72) fl_mm
 * @Double(label="spherical aberration in mm",value=1.2) C_s_mm
 * 
 * [1] Jürgen Thomas and Thomas Gemming, Analytische Transmissionselektronenmikroskopie, Springer 2013
 */

importClass(Packages.ij.ImagePlus);
importClass(Packages.ij.IJ);
 
importPackage(Packages.org.jfree.chart);
importPackage(Packages.org.jfree.chart.plot);
importPackage(Packages.org.jfree.chart.axis);
importPackage(Packages.org.jfree.data.xy);
importPackage(Packages.org.jfree.chart.renderer.xy);
importPackage(Packages.org.jfree.chart.annotations);
importPackage(Packages.org.jfree.ui);

importPackage(Packages.java.awt);

var C_s = C_s_mm * 1e-3;
var fl = fl_mm * 1e-3;
var h = 4.135667516e-15;
var e = 1;
var U = U_kV * 1e3;
var c = 299792458;
var m_0 = 510998.928 / Math.pow(c, 2);
// [1] Gl. 1.18
var lambda = h / Math.sqrt(e * U * (2 * m_0 + e * U / Math.pow(c, 2)));
// [1] Gl. 10.5.5 
var alpha_opt = 0.77 *  Math.pow(lambda / C_s, 0.25) * 1e3;

var chart = createChart();
addAnnotations(chart);

bi = chart.createBufferedImage(1200, 900); 
imp = new ImagePlus("Objective aperture chart", bi);
imp.show();

function createChart() {
	var chart = ChartFactory.createXYLineChart(
		"Objective aperture",
		"aperture diameter [µm]",
		"error disk diameter [nm]",
		createDataset(),
		PlotOrientation.VERTICAL,
		true,
		true,
		false
	);
	
	var plot = chart.getPlot();
	var rangeAxis = plot.getRangeAxis();
	rangeAxis.setAutoRange(false);
	rangeAxis.setUpperBound(2.0);
	
	var renderer = new XYLineAndShapeRenderer();
	renderer.setSeriesPaint(0, Color.RED);
	renderer.setSeriesPaint(1, Color.GREEN);
	renderer.setSeriesPaint(2, Color.BLUE);
	renderer.setSeriesStroke(0, new BasicStroke(2.0));
	renderer.setSeriesShapesVisible(0, false);
	renderer.setSeriesShapesVisible(1, false);
	renderer.setSeriesShapesVisible(2, false);
	plot.setRenderer(renderer);
	return chart;
}

function addAnnotations(chart) {
	var plot = chart.getPlot();
	
	var x_opt = fromRad(alpha_opt);
	// [1] Gl. 2.18
	var y_opt = 0.9 * Math.pow(C_s * Math.pow(lambda, 3), 0.25) * 1e9;
	var line = new XYLineAnnotation(0, y_opt, fromRad(Math.ceil(2 * alpha_opt)), y_opt);
	plot.addAnnotation(line);
	
	var pointer = new XYPointerAnnotation(
		"Smallest error disc: " + y_opt.toPrecision(2) + " nm @ " + x_opt.toFixed(1) + " µm",
		x_opt,
		y_opt,
		5.0 * Math.PI / 4.0
	);
	stylePointer(pointer);
	plot.addAnnotation(pointer);
	var aperture_alpha = 0.5 * 20 * 1e-6 / fl;
	var resolution = new XYPointerAnnotation(
		"Resolution with " + fromRad(aperture_alpha * 1e3).toFixed(0) + " µm aperture: " + deltaResulting(aperture_alpha).toPrecision(2) * 1e9 + " nm",
		fromRad(aperture_alpha * 1e3),
		deltaResulting(aperture_alpha) * 1e9,
		1.5 * Math.PI / 4.0
	);
	stylePointer(resolution);
	
	plot.addAnnotation(resolution);
}

function stylePointer(pointer) {
	pointer.setLabelOffset(15);
	pointer.setBaseRadius(50.0);
	pointer.setTipRadius(5);
	pointer.setFont(new Font("SansSerif", Font.PLAIN, 12));
	pointer.setPaint(Color.blue);
	pointer.setTextAnchor(TextAnchor.HALF_ASCENT_CENTER);
}

function createDataset() {
	var dataset = new XYSeriesCollection();
	var all = new XYSeries("resulting error disc");
	var s = new XYSeries("spherical aberration");
	var b = new XYSeries("diffraction limit");
	var start = 0;
	var stop = Math.ceil(2 * alpha_opt);
	var steps = 100;
	var step = 1. * stop / steps;
	for (var i = 0; i <= steps; i++) {
		var x = (step * i + start) * 1e-3;
		var x_val = fromRad(step * i + start);
		s.add(x_val, deltaSpherical(x) * 1e9);
		b.add(x_val, deltaDiffraction(x) * 1e9);
		var delta = deltaResulting(x);
		all.add(x_val, delta * 1e9);
	}
	dataset.addSeries(all);
	dataset.addSeries(s);
	dataset.addSeries(b);
	return dataset;
}

function deltaSpherical(x) {
	// [1] Gl. 2.16
	var val = C_s * Math.pow(x, 3);
	return val;
}

function deltaDiffraction(x) {
	// [1] Gl. 2.16
	var val = 0.61 * lambda / x;
	return val;
}

function deltaResulting(x) {
	// [1] Gl. 2..17
	var val = Math.sqrt(Math.pow(deltaSpherical(x), 2) + Math.pow(deltaDiffraction(x), 2));
	return val;
}

function fromRad(alpha) {
	var d = 2 * alpha * fl * 1e3;
	return d;
}