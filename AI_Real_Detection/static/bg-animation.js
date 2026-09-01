/**
 * Background Particle Animation
 * Creates a "living" grid of particles that reacts to mouse movement.
 */

const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');

let particlesArray;

// Mouse Interactions
let mouse = {
    x: null,
    y: null,
    radius: 150 // Interaction radius
}

window.addEventListener('mousemove', function (event) {
    mouse.x = event.x;
    mouse.y = event.y;
});

// Particle Class
class Particle {
    constructor(x, y, loadingSpeed, size, color) {
        this.x = x;
        this.y = y;
        this.baseX = x; // Remember original position
        this.baseY = y;
        this.size = size;
        this.color = color;
        this.density = (Math.random() * 30) + 1; // How heavy/slow it moves
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = this.color;
        ctx.fill();
    }

    update() {
        // Mouse Interaction Physics
        let dx = mouse.x - this.x;
        let dy = mouse.y - this.y;
        let distance = Math.sqrt(dx * dx + dy * dy);
        let forceDirectionX = dx / distance;
        let forceDirectionY = dy / distance;
        let maxDistance = mouse.radius;
        let force = (maxDistance - distance) / maxDistance;
        let directionX = forceDirectionX * force * this.density;
        let directionY = forceDirectionY * force * this.density;

        if (distance < mouse.radius) {
            // Move away from mouse (Repulsion) - feels "magnetic"
            this.x -= directionX;
            this.y -= directionY;
            // Option: To make it attract instead, change -= to +=
        } else {
            // Return to original position (Elasticity)
            if (this.x !== this.baseX) {
                let dx = this.x - this.baseX;
                this.x -= dx / 10; // Speed of return
            }
            if (this.y !== this.baseY) {
                let dy = this.y - this.baseY;
                this.y -= dy / 10;
            }
        }
    }
}

function init() {
    particlesArray = [];
    // Create a grid of particles
    const numberOfParticles = (canvas.width * canvas.height) / 9000; // Density control

    // Random distribution (Starfield style)
    for (let i = 0; i < numberOfParticles * 2; i++) {
        let size = (Math.random() * 2) + 0.5; // Random size
        let x = Math.random() * innerWidth;
        let y = Math.random() * innerHeight;
        let color = '#00DC82'; // Brand Green

        particlesArray.push(new Particle(x, y, 1, size, color));
    }
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, innerWidth, innerHeight);

    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].draw();
        particlesArray[i].update();
    }
    // Connect particles with lines (Constellation effect) - Optional, can be heavy
    // connect(); 
}

// Handle Resize
window.addEventListener('resize', function () {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
    mouse.radius = ((canvas.height / 80) * (canvas.height / 80));
    init();
});

// Start
canvas.width = innerWidth;
canvas.height = innerHeight;
init();
animate();
