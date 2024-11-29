const backgroundSketch = (p) => {
  let particles = [];
  const numParticles = 70;
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
    p.frameRate(30);
    p.colorMode(p.RGB, 255, 255, 255, 1);
    
    // Initialize particles
    for (let i = 0; i < numParticles; i++) {
      let selectedColor = p.random([
        [3, 206, 164],  // mint
        [234, 196, 53], // saffron
        [228, 0, 102]   // razzmatazz
      ]);

      particles.push({
        pos: p.createVector(p.random(p.width), p.random(p.height)),
        vel: p.createVector(0, 0),
        size: p.random(2, 5),
        color: {
          r: selectedColor[0],
          g: selectedColor[1],
          b: selectedColor[2],
          alpha: p.random(.2, .5) // Transparencia
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
      particle.vel.limit(3);
      particle.pos.add(particle.vel);
      
      particle.pos.x = (particle.pos.x + p.width) % p.width;
      particle.pos.y = (particle.pos.y + p.height) % p.height;
      
      let trailLength = 15;
      
      for (let i = 0; i < trailLength; i++) {
        let trailPos = p.createVector(
          particle.pos.x - particle.vel.x * i * 0.5,
          particle.pos.y - particle.vel.y * i * 0.5
        );
        
        let positions = getWrappedPositions(trailPos.x, trailPos.y, p);
        
        positions.forEach(pos => {
          p.noStroke();
          p.fill(particle.color.r, particle.color.g, particle.color.b, particle.color.alpha);
          p.circle(pos.x, pos.y, particle.size * (1 - i/trailLength));
        });
      }
    });
    
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
};

// Create a new p5 instance
new p5(backgroundSketch);
