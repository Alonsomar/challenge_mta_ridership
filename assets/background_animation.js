// The p5.js script that creates the moving canvas animation for the background.
// Example p5.js background animation
let x = 0;

function setup() {
    let canvas = createCanvas(windowWidth, windowHeight);
    canvas.position(0, 0);
    canvas.style('z-index', '-1');
}

function draw() {
    background(30);
    fill(255);
    ellipse(x, height / 2, 50, 50);
    x += 1;
    if (x > width) {
        x = 0;
    }
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
