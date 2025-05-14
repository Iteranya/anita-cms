// effects.js - Visual effects and animations
/**
 * Set up visual effects and animations
 */
export function setupEffects() {
    // Add CSS animations
    addAnimationStyles();
    
    // Set up the flower trail effect on mouse move
    document.addEventListener('mousemove', createFlowerTrail);
}

/**
 * Create a flower trail effect following the mouse
 * @param {MouseEvent} e - Mouse event
 */
function createFlowerTrail(e) {
    const flower = document.createElement('div');
    flower.innerHTML = '✿';
    flower.style.position = 'fixed';
    flower.style.left = e.clientX + 'px';
    flower.style.top = e.clientY + 'px';
    flower.style.color = `hsl(${Math.random() * 60 + 150}, 70%, 60%)`;
    flower.style.fontSize = Math.random() * 20 + 10 + 'px';
    flower.style.pointerEvents = 'none';
    flower.style.zIndex = '100';
    flower.style.transform = 'translate(-50%, -50%)';
    flower.style.animation = 'float-up 1s ease-out forwards';
    
    document.body.appendChild(flower);
    
    setTimeout(() => {
        flower.remove();
    }, 1000);
}

/**
 * Add animation styles to the document
 */
function addAnimationStyles() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInOut {
            0% { opacity: 0; transform: translateX(-50%) translateY(20px); }
            20% { opacity: 1; transform: translateX(-50%) translateY(0); }
            80% { opacity: 1; transform: translateX(-50%) translateY(0); }
            100% { opacity: 0; transform: translateX(-50%) translateY(-20px); }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        @keyframes float-up {
            to {
                transform: translate(-50%, -100px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}