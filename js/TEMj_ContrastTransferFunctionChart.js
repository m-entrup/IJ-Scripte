/*
 * @Double(label="Voltage in keV",value=200) U_kV
 * @Double(label="spherical aberration in mm",value=1.2) C_s_mm
 * @Double(label="chromatic aberration in mm",value=1.2) C_c_mm
 * @Double(label="energy spread in eV",value=0.7) dU
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
var C_c = C_c_mm * 1e-3;
var h = 4.135667516e-15;
var e = 1;
var U = U_kV * 1e3;
var c = 299792458;
var m_0 = 510998.928 / Math.pow(c, 2);
// [1] Gl. 1.18
var lambda = h / Math.sqrt(e * U * (2 * m_0 + e * U / Math.pow(c, 2)));
var df_opt = Math.sqrt(2. * C_s * lambda);

var chart = createChart();
addAnnotations(chart);

bi = chart.createBufferedImage(1200, 900); 
imp = new ImagePlus("Contrast transfer function chart", bi);
imp.show();


function addAnnotations(chart) {
	var plot = chart.getPlot();

	// [1] Gl. 10.14.26
	var x_opt = Math.sqrt(Math.sqrt(2) / (Math.PI * C_c * dU / U * e * lambda)) * 1e-9;
	var pointer = new XYPointerAnnotation(
		"Information limit (1/e²) at: " + x_opt.toPrecision(2) + " \u215Fnm",
		x_opt,
		0,
		-1.0 * Math.PI / 4.0
	);	
	stylePointer(pointer);
	pointer.setTextAnchor(TextAnchor.HALF_ASCENT_LEFT);
	plot.addAnnotation(pointer);

	// [1] Gl. 10.15.3
	var x_opt2 = Math.sqrt(2*df_opt / (C_s * Math.pow(lambda, 2))) * 1e-9;
	// IJ.log(x_opt2);
	var pointer2 = new XYPointerAnnotation(
		"contrast inversion at: " + x_opt2.toPrecision(2) + " \u215Fnm",
		x_opt2,
		0,
		-3.0 * Math.PI / 4.0
	);	
	stylePointer(pointer2);
	pointer2.setTextAnchor(TextAnchor.HALF_ASCENT_RIGHT);
	plot.addAnnotation(pointer2);	
}

function stylePointer(pointer) {
	pointer.setLabelOffset(15);
	pointer.setBaseRadius(50.0);
	pointer.setTipRadius(5);
	pointer.setFont(new Font("SansSerif", Font.PLAIN, 12));
	pointer.setPaint(Color.blue);
	pointer.setTextAnchor(TextAnchor.HALF_ASCENT_CENTER);
}

function createChart() {
	var chart = ChartFactory.createXYLineChart(
		"Contrast transfer function",
		"spatial frequency q [1/nm]",
		"relative contrast",
		createDataset(),
		PlotOrientation.VERTICAL,
		true,
		true,
		false
	);
	
	var plot = chart.getPlot();
	var rangeAxis = plot.getRangeAxis();
	
	var renderer = new XYLineAndShapeRenderer();
	renderer.setSeriesPaint(0, Color.RED);
	renderer.setSeriesPaint(1, Color.GREEN);
	renderer.setSeriesShapesVisible(0, false);
	renderer.setSeriesShapesVisible(1, false);
	plot.setRenderer(renderer);
	return chart;
}

function createDataset() {
	var dataset = new XYSeriesCollection();

	var ctf_opt = new XYSeries("CTF @ " + (df_opt * 1e9).toFixed(1) + " nm defocus");
	var ctf_0 = new XYSeries("CTF @ 0 nm defocus");
	var start = 0;
	var stop = 10;
	var steps = 1000;
	var step = 1. * stop / steps;
	for (var i = 0; i <= steps; i++) {
		var x = (step * i + start) * 1e9;
		var x_val = (step * i + start);
		ctf_opt.add(x_val, ctf(x, df_opt));
		ctf_0.add(x_val, ctf(x, 0));
	}
	dataset.addSeries(ctf_opt);
	dataset.addSeries(ctf_0);
	return dataset;
}

function ctf(x, df) {
	// [1] Gl. 10.14.25
	var value = Math.sin(0.5 * Math.PI
		* (C_s * Math.pow(lambda, 3) * Math.pow(x, 4) - 2. * df * lambda * Math.pow(x, 2)))
		* Math.exp(-Math.pow(Math.PI, 2) * Math.pow(C_c, 2) * Math.pow(dU / U, 2) * Math.pow(lambda, 2)
		* Math.pow(x, 4));
	return value;
}