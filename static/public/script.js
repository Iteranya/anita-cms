// Intersection Observer for animation when elements enter viewport
document.addEventListener('DOMContentLoaded', function() {
    // Add observer for images
    const images = document.querySelectorAll('img');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'scale(1)';
                }, 100);
                imageObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    images.forEach(img => {
        img.style.opacity = '0';
        img.style.transform = 'scale(0.95)';
        imageObserver.observe(img);
    });

    // Add hover effect to code blocks
    const codeBlocks = document.querySelectorAll('pre');
    codeBlocks.forEach(block => {
        block.addEventListener('mouseenter', () => {
            block.style.transform = 'translateY(-2px)';
            block.style.boxShadow = 'inset 0 1px 5px rgba(0,0,0,0.3), 0 5px 15px rgba(0,0,0,0.2)';
        });
        block.addEventListener('mouseleave', () => {
            block.style.transform = 'translateY(0)';
            block.style.boxShadow = 'inset 0 1px 5px rgba(0,0,0,0.3)';
        });
    });

    // When h2 is in view, animate it
    const headers = document.querySelectorAll('h2');
    const headerObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                }, 100);
                headerObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    headers.forEach(header => {
        header.style.opacity = '0';
        headerObserver.observe(header);
    });
    
    // Special animation for the warning section
    const warningSection = document.querySelector('.warning');
    if (warningSection) {
        warningSection.style.transition = 'all 0.5s ease';
        
        setInterval(() => {
            warningSection.style.borderLeftColor = '#ff6464';
            setTimeout(() => {
                warningSection.style.borderLeftColor = '#ff9c64';
            }, 1000);
        }, 2000);
    }
});