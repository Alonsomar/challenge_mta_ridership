const backgroundSketch = (p) => {
  let flowfield;
  let particles = [];
  const numParticles = 150;
  let noiseScale = 0.005;
  let noiseStrength = 1;
  let hueOffset = 0;

  p.setup = () => {
    let canvas = p.createCanvas(p.windowWidth, p.windowHeight);
    canvas.style('position', 'fixed');
    canvas.style('top', '0');
    canvas.style('left', '0');
    canvas.style('z-index', '-1');
    canvas.style('pointer-events', 'none');
    p.colorMode(p.HSB, 360, 100, 100, 1);
    
    // Initialize particles
    for (let i = 0; i < numParticles; i++) {
      particles.push({
        pos: p.createVector(p.random(p.width), p.random(p.height)),
        vel: p.createVector(0, 0),
        size: p.random(1, 3),
        color: {
          h: p.random([
            p.color(3, 206, 164),  // mint
            p.color(234, 196, 53), // saffron
            p.color(228, 0, 102),  // razzmatazz
          ]),
          alpha: p.random(0.1, 0.3)
        }
      });
    }
  };

  p.draw = () => {
    p.clear();
    hueOffset += 0.1;
    
    particles.forEach(particle => {
      let angle = p.noise(particle.pos.x * noiseScale, 
                       particle.pos.y * noiseScale, 
                       p.frameCount * 0.002) * p.TWO_PI * 2;
      
      let direction = p5.Vector.fromAngle(angle);
      direction.mult(noiseStrength);
      
      particle.vel.add(direction);
      particle.vel.limit(2);
      particle.pos.add(particle.vel);
      
      particle.pos.x = (particle.pos.x + p.width) % p.width;
      particle.pos.y = (particle.pos.y + p.height) % p.height;
      
      let trailLength = 20;
      let trailAlpha = particle.color.alpha;
      
      for (let i = 0; i < trailLength; i++) {
        let trailPos = p.createVector(
          particle.pos.x - particle.vel.x * i * 0.5,
          particle.pos.y - particle.vel.y * i * 0.5
        );
        
        let positions = getWrappedPositions(trailPos.x, trailPos.y, p);
        
        positions.forEach(pos => {
          p.noStroke();
          p.fill(particle.color.h, trailAlpha * (1 - i/trailLength));
          p.circle(pos.x, pos.y, particle.size * (1 - i/trailLength));
        });
      }
    });
    
    drawVignette(p);
  };

  p.windowResized = () => {
    p.resizeCanvas(p.windowWidth, p.windowHeight);
  };

  function getWrappedPositions(x, y, p) {
    let positions = [];
    let offsets = [-1, 0, 1];
    
    offsets.forEach(offsetX => {
      offsets.forEach(offsetY => {
        positions.push({
          x: x + offsetX * p.width,
          y: y + offsetY * p.height
        });
      });
    });
    
    return positions.filter(pos => {
      return pos.x > -50 && pos.x < p.width + 50 &&
             pos.y > -50 && pos.y < p.height + 50;
    });
  }

  function drawVignette(p) {
    let gradient = p.drawingContext.createRadialGradient(
      p.width/2, p.height/2, 0,
      p.width/2, p.height/2, p.width/2
    );
    gradient.addColorStop(0, 'rgba(245, 247, 250, 0)');
    gradient.addColorStop(1, 'rgba(235, 240, 245, 0.8)');
    
    p.drawingContext.fillStyle = gradient;
    p.noStroke();
    p.rect(0, 0, p.width, p.height);
  }
};

// Create a new p5 instance
new p5(backgroundSketch);
