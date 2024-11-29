const trainSketch = (p) => {
    let angle = 0;
    let train = [];
    let smoke = [];
    let rails = [];
    let vibrationOffset = {x: 0, y: 0};
    let vibrationAngle = 0;

    const styles = getComputedStyle(document.documentElement);
    const COLORS = {
        tomato: styles.getPropertyValue('--tomato').trim(),
        razzmatazz: styles.getPropertyValue('--razzmatazz').trim(),
        mint: styles.getPropertyValue('--mint').trim(),
        saffron: styles.getPropertyValue('--saffron').trim(),
        yinmnBlue: styles.getPropertyValue('--yinmn-blue').trim()
    };

    p.setup = () => {
        let container = document.getElementById('train-canvas-container');
        if (container) {
            let canvas = p.createCanvas(container.offsetWidth, container.offsetHeight);
            canvas.parent('train-canvas-container');
            
            p.frameRate(30);
            p.pixelDensity(1);
            
            let minDim = Math.min(container.offsetWidth, container.offsetHeight);
            trainScale = minDim / 200;
            
            // Inicializar los rieles con segmentos
            for (let i = 0; i < 360; i += 5) {
                let rad = p.radians(i);
                rails.push({
                    x: p.cos(rad),
                    y: p.sin(rad)
                });
            }

            // Inicializar el tren con espaciado fijo
            let spacing = 0.3;
            for (let i = 0; i < 5; i++) {
                train.push({
                    x: 0,
                    y: 0,
                    angle: -i * spacing,
                    type: i === 0 ? 'locomotive' : 'wagon'
                });
            }
        }
    };

    p.windowResized = () => {
        let container = document.getElementById('train-canvas-container');
        if (container) {
            p.resizeCanvas(container.offsetWidth, container.offsetHeight);
        }
    };

    p.draw = () => {
        const centerX = p.width / 2;
        const centerY = p.height / 2;

        p.clear();
        p.background(255, 0);
        p.push();
        p.translate(centerX, centerY);
        
        drawRails();
        updateTrain();
        updateSmoke();
        
        p.pop();
    };

    function updateTrain() {
        let radiusX = 250;
        let radiusY = 250;

        vibrationAngle += 0.2;
        vibrationOffset = {
            x: p.cos(vibrationAngle) * 0.5,
            y: p.sin(vibrationAngle * 1.5) * 0.3
        };
        
        for (let i = 0; i < train.length; i++) {
            let t = angle - i * 0.3;
            
            let x = p.cos(t) * radiusX;
            let y = p.sin(t) * radiusY;
            
            let speed = 0.02;
            let vibrationIntensity = p.map(speed, 0, 0.05, 0, 1);
            
            x += vibrationOffset.x * vibrationIntensity;
            y += vibrationOffset.y * vibrationIntensity;
            
            let rotationAngle = t + p.PI/2;
            rotationAngle += p.sin(vibrationAngle) * 0.01;
            
            train[i].x = x;
            train[i].y = y;
            train[i].angle = rotationAngle;
            
            if (train[i].type === 'locomotive') {
                drawLocomotive(x, y, rotationAngle);
                
                if (i === 0 && p.frameCount % 1 === 0) {
                    smoke.push({
                        x: x + p.cos(rotationAngle) * 25 + vibrationOffset.x,
                        y: y + p.sin(rotationAngle) * 0 + vibrationOffset.y,
                        size: p.random(2, 25),
                        alpha: 120 + p.random()*50,
                        vx: p.random(-0.8, 0.8),
                        vy: p.random(-0.8, 0.8),
                        color_rand: 80 + p.random()*120
                    });
                }
            } else {
                drawWagon(x, y, rotationAngle);
            }
        }
        
        angle += 0.02;
    }

    function drawRails() {
        let radius = 250;
        
        p.noFill();
        p.strokeWeight(8);
        p.stroke(200, 200, 200, 30);
        p.ellipse(2, 2, radius * 2 + 20, radius * 2 + 20);
        
        p.stroke(150);
        p.strokeWeight(4);
        for (let i = 0; i < 360; i += 5) {
            let rad = p.radians(i);
            let x1 = p.cos(rad) * (radius - 15);
            let y1 = p.sin(rad) * (radius - 15);
            let x2 = p.cos(rad) * (radius + 15);
            let y2 = p.sin(rad) * (radius + 15);
            
            p.stroke(100);
            p.line(x1, y1, x2, y2);
            p.stroke(180);
            p.line(x1+1, y1+1, x2+1, y2+1);
        }
        
        for (let offset = -10; offset <= 10; offset += 20) {
            p.stroke(80);
            p.strokeWeight(3);
            p.noFill();
            p.beginShape();
            for (let i = 0; i < 360; i += 5) {
                let rad = p.radians(i);
                let x = p.cos(rad) * (radius + offset);
                let y = p.sin(rad) * (radius + offset);
                p.vertex(x, y);
            }
            p.endShape(p.CLOSE);
            
            p.stroke(200, 200, 200, 30);
            p.strokeWeight(1);
            p.beginShape();
            for (let i = 0; i < 360; i += 5) {
                let rad = p.radians(i);
                let x = p.cos(rad) * (radius + offset) + 1;
                let y = p.sin(rad) * (radius + offset) + 1;
                p.vertex(x, y);
            }
            p.endShape(p.CLOSE);
        }
    }

    function drawLocomotive(x, y, angle) {
        p.push();
        p.translate(x, y);
        p.rotate(angle);
        
        let shadowOffset = p.map(p.sin(p.frameCount * 0.1), -1, 1, 1, 3);
        shadowOffset += p.abs(vibrationOffset.y) * 2;
        p.fill(220, 220, 220, 100);
        p.noStroke();
        p.ellipse(shadowOffset + vibrationOffset.x, shadowOffset + vibrationOffset.y, 75, 48);
        
        p.fill(30);
        p.stroke(40);
        p.strokeWeight(2);
        p.rect(-40, -15, 60, 30, 5);
        
        p.fill(200);
        p.noStroke();
        p.rect(-38, -13, 56, 2, 1);
        p.rect(-38, 11, 56, 2, 1);
        
        p.fill(40);
        p.beginShape();
        p.vertex(20, -15);
        p.vertex(35, -8);
        p.vertex(35, 8);
        p.vertex(20, 15);
        p.endShape(p.CLOSE);
        
        p.fill(50);
        p.rect(-35, -18, 25, 36, 3);
        
        p.fill(220, 220, 255, 200);
        p.rect(-30, -13, 8, 8, 1);
        p.rect(-30, 5, 8, 8, 1);
        
        p.fill(255, 255, 255, 150);
        p.rect(-29, -12, 2, 6);
        p.rect(-29, 6, 2, 6);
        
        p.fill(40);
        p.rect(25, -8, 8, 16, 2);
        
        let pulseIntensity = p.map(p.sin(p.frameCount * 0.1), -1, 1, 100, 255);
        p.fill(255, 255, 200, pulseIntensity);
        p.ellipse(35, 0, 6, 6);
        
        let glowIntensity = p.map(p.sin(p.frameCount * 0.1), -1, 1, 30, 80);
        p.fill(255, 255, 200, glowIntensity);
        p.noStroke();
        p.ellipse(35, 0, 20, 20);
        
        p.stroke(200);
        p.strokeWeight(1);
        p.line(-35, -14, 15, -14);
        p.line(-35, 14, 15, 14);
        
        p.pop();
    }

    function drawWagon(x, y, angle) {
        p.push();
        p.translate(x, y);
        p.rotate(angle);
        
        let shadowOffset = p.map(p.sin(p.frameCount * 0.1), -1, 1, 1, 3);
        shadowOffset += p.abs(vibrationOffset.y) * 2;
        p.fill(220, 220, 220, 100);
        p.noStroke();
        p.ellipse(shadowOffset + vibrationOffset.x, shadowOffset + vibrationOffset.y, 70, 43);
        
        p.fill(p.color(COLORS.tomato));
        p.stroke(p.color(COLORS.razzmatazz));
        p.strokeWeight(2);
        p.rect(-35, -15, 50, 30, 4);
        
        p.fill(200);
        p.noStroke();
        p.rect(-33, -13, 46, 2, 1);
        p.rect(-33, 11, 46, 2, 1);
        
        p.fill(p.color(COLORS.yinmnBlue + '40'));
        p.noStroke();
        p.rect(-31, -11, 42, 22, 2);
        
        p.fill(40);
        p.stroke(60);
        p.rect(-40, -4, 10, 8, 1);
        p.rect(15, -4, 10, 8, 1);
        
        p.noStroke();
        p.fill(255, 255, 255, 30);
        p.rect(-31, -10, 42, 5, 1);
        
        p.pop();
    }

    function updateSmoke() {
        for (let i = smoke.length - 1; i >= 0; i--) {
            let particle = smoke[i];
            particle.x += particle.vx;
            particle.y += particle.vy;
            particle.size += 0.3;
            particle.alpha -= 3;
            
            if (particle.alpha <= 0) {
                smoke.splice(i, 1);
            } else {
                p.noStroke();
                for(let j = 0; j < 2; j++) {
                    let alpha = particle.alpha * (1 - j/2);
                    p.fill(particle.color_rand, particle.color_rand, particle.color_rand, alpha);
                    p.ellipse(
                        particle.x + p.random(-1,1)*0.5, 
                        particle.y + p.random(-1,1)*0.5, 
                        particle.size + j*2, 
                        particle.size + j*2
                    );
                }
            }
        }
    }


};

document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        new p5(trainSketch);
    }, 300);
});


