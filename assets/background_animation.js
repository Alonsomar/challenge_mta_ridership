// The p5.js script that creates the moving canvas animation for the background.
// Example p5.js background animation
let flowfield;
let particles = [];
const numParticles = 150;
let noiseScale = 0.005;
let noiseStrength = 1;
let hueOffset = 0;

function setup() {
    let canvas = createCanvas(windowWidth, windowHeight);
    canvas.style('position', 'fixed');
    canvas.style('top', '0');
    canvas.style('left', '0');
    canvas.style('z-index', '-1');
    canvas.style('pointer-events', 'none');
    colorMode(HSB, 360, 100, 100, 1);
    
    // Inicializar partículas
    for (let i = 0; i < numParticles; i++) {
        particles.push({
            pos: createVector(random(width), random(height)),
            vel: createVector(0, 0),
            size: random(1, 3),
            color: {
                h: random([
                    color(3, 206, 164),  // mint
                    color(234, 196, 53), // saffron
                    color(228, 0, 102),  // razzmatazz
                ]),
                alpha: random(0.1, 0.3)
            }
        });
    }
}

function draw() {
    clear();
    hueOffset += 0.1;
    
    // Actualizar y dibujar partículas
    particles.forEach(particle => {
        // Calcular dirección basada en noise field
        let angle = noise(particle.pos.x * noiseScale, 
                         particle.pos.y * noiseScale, 
                         frameCount * 0.002) * TWO_PI * 2;
        
        // Crear vector de dirección
        let direction = p5.Vector.fromAngle(angle);
        direction.mult(noiseStrength);
        
        // Aplicar fuerza
        particle.vel.add(direction);
        particle.vel.limit(2);
        particle.pos.add(particle.vel);
        
        // Efecto toroidal (canvas infinito)
        particle.pos.x = (particle.pos.x + width) % width;
        particle.pos.y = (particle.pos.y + height) % height;
        
        // Dibujar estelas con efecto envolvente
        let trailLength = 20;
        let trailAlpha = particle.color.alpha;
        
        for (let i = 0; i < trailLength; i++) {
            let trailPos = createVector(
                particle.pos.x - particle.vel.x * i * 0.5,
                particle.pos.y - particle.vel.y * i * 0.5
            );
            
            // Aplicar efecto toroidal a las estelas también
            let positions = getWrappedPositions(trailPos.x, trailPos.y);
            
            positions.forEach(pos => {
                noStroke();
                fill(particle.color.h, trailAlpha * (1 - i/trailLength));
                circle(pos.x, pos.y, particle.size * (1 - i/trailLength));
            });
        }
    });
    
    // Efecto de viñeta
    drawVignette();
}

// Función para obtener todas las posiciones envolventes necesarias
function getWrappedPositions(x, y) {
    let positions = [];
    let offsets = [-1, 0, 1];
    
    offsets.forEach(offsetX => {
        offsets.forEach(offsetY => {
            positions.push({
                x: x + offsetX * width,
                y: y + offsetY * height
            });
        });
    });
    
    // Filtrar solo las posiciones cercanas al viewport
    return positions.filter(pos => {
        return pos.x > -50 && pos.x < width + 50 &&
               pos.y > -50 && pos.y < height + 50;
    });
}

function drawVignette() {
    let gradient = drawingContext.createRadialGradient(
        width/2, height/2, 0,
        width/2, height/2, width/2
    );
    gradient.addColorStop(0, 'rgba(245, 247, 250, 0)');
    gradient.addColorStop(1, 'rgba(235, 240, 245, 0.8)');
    
    drawingContext.fillStyle = gradient;
    noStroke();
    rect(0, 0, width, height);
}

function windowResized() {
    resizeCanvas(windowWidth, windowHeight);
}
