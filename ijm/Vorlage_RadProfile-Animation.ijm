w = getWidth();
h = getHeight();
c_x = w/2;
c_y = h/2;

ang = 0;
length = (w + h) / 8;

function x_pos(angle) {
	return length * cos(angle / 180 * PI);
}

function y_pos(angle) {
	return length * sin(angle / 180 * PI);
}

function set_line(angle) {	
	makeLine(c_x, c_y, c_x + x_pos(angle), c_y + y_pos(angle));
}
set_line(ang)
run("Plot Profile");
waitForUser("Activate Live mode");

while (ang < 720) {
	ang++;
	wait(500);
	set_line(ang);
}
