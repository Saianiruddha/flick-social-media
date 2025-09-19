/* ========================================
   FLICK - Interactive Animations & Effects
   Dynamic, Quick, and Engaging JavaScript
   ======================================== */

document.addEventListener('DOMContentLoaded', function() {
    // FLICK Animation System
    const FlickAnimations = {
        
        // Initialize all FLICK animations
        init: function() {
            this.setupLikeAnimations();
            this.setupPostCardAnimations();
            this.setupNavbarAnimations();
            this.setupFormAnimations();
            this.setupScrollEffects();
            this.setupQuickFlickEffects();
            console.log('🚀 FLICK Animations initialized!');
        },

        // Enhanced Like Button Animations
        setupLikeAnimations: function() {
            document.querySelectorAll('.action-btn').forEach(btn => {
                if (btn.querySelector('i') && btn.querySelector('i').classList.contains('bi-heart')) {
                    btn.addEventListener('click', function(e) {
                        // Create heart explosion effect
                        this.createHeartExplosion(e.currentTarget);
                        
                        // Add extra bounce
                        e.currentTarget.style.transform = 'scale(1.3)';
                        setTimeout(() => {
                            e.currentTarget.style.transform = '';
                        }, 200);
                    }.bind(this));
                }
            });
        },

        // Heart explosion effect for likes
        createHeartExplosion: function(button) {
            const hearts = ['💖', '💕', '💘', '💝', '❤️', '🧡', '💛'];
            const rect = button.getBoundingClientRect();
            
            for (let i = 0; i < 6; i++) {
                const heart = document.createElement('span');
                heart.innerHTML = hearts[Math.floor(Math.random() * hearts.length)];
                heart.className = 'flick-heart-explosion';
                
                // Position at button center
                heart.style.position = 'fixed';
                heart.style.left = rect.left + rect.width/2 + 'px';
                heart.style.top = rect.top + rect.height/2 + 'px';
                heart.style.pointerEvents = 'none';
                heart.style.zIndex = '9999';
                heart.style.fontSize = '16px';
                
                // Random direction and distance
                const angle = (i / 6) * Math.PI * 2;
                const distance = 50 + Math.random() * 30;
                const targetX = Math.cos(angle) * distance;
                const targetY = Math.sin(angle) * distance;
                
                document.body.appendChild(heart);
                
                // Animate
                heart.animate([
                    { 
                        transform: 'translate(-50%, -50%) scale(0) rotate(0deg)',
                        opacity: 1
                    },
                    { 
                        transform: `translate(calc(-50% + ${targetX}px), calc(-50% + ${targetY}px)) scale(1) rotate(360deg)`,
                        opacity: 0
                    }
                ], {
                    duration: 800 + Math.random() * 400,
                    easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
                }).onfinish = () => heart.remove();
            }
        },

        // Post Card Hover Effects
        setupPostCardAnimations: function() {
            document.querySelectorAll('.post-card, .card').forEach(card => {
                // Magnetic effect on mouse move
                card.addEventListener('mousemove', function(e) {
                    if (!card.classList.contains('flick-magnetic-disabled')) {
                        const rect = card.getBoundingClientRect();
                        const x = e.clientX - rect.left - rect.width / 2;
                        const y = e.clientY - rect.top - rect.height / 2;
                        
                        card.style.transform = `perspective(1000px) rotateY(${x / 10}deg) rotateX(${-y / 10}deg) translateY(-2px)`;
                    }
                });
                
                card.addEventListener('mouseleave', function() {
                    card.style.transform = '';
                });
                
                // Add shimmer effect on hover
                card.addEventListener('mouseenter', function() {
                    if (!card.querySelector('.flick-shimmer')) {
                        const shimmer = document.createElement('div');
                        shimmer.className = 'flick-shimmer';
                        shimmer.innerHTML = '<div class="flick-shimmer-line"></div>';
                        card.appendChild(shimmer);
                        
                        setTimeout(() => shimmer.remove(), 600);
                    }
                });
            });
        },

        // Navbar scroll effects
        setupNavbarAnimations: function() {
            let lastScrollTop = 0;
            const navbar = document.querySelector('.navbar');
            
            window.addEventListener('scroll', function() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down
                    navbar.style.transform = 'translateY(-100%)';
                } else {
                    // Scrolling up
                    navbar.style.transform = 'translateY(0)';
                }
                
                // Add blur effect based on scroll
                const blurAmount = Math.min(scrollTop / 200, 1) * 20;
                navbar.style.backdropFilter = `blur(${blurAmount}px)`;
                
                lastScrollTop = scrollTop <= 0 ? 0 : scrollTop;
            }, { passive: true });
        },

        // Form interaction effects
        setupFormAnimations: function() {
            // Enhanced form focus effects
            document.querySelectorAll('input, textarea').forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.classList.add('flick-form-focused');
                    this.createFocusRipple();
                }.bind(this));
                
                input.addEventListener('blur', function() {
                    this.parentElement.classList.remove('flick-form-focused');
                });
            });
        },

        // Create focus ripple effect
        createFocusRipple: function() {
            // Implementation would go here for focus ripples
        },

        // Scroll-triggered animations
        setupScrollEffects: function() {
            const observerOptions = {
                root: null,
                rootMargin: '0px',
                threshold: 0.1
            };

            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('flick-scroll-reveal');
                        
                        // Add staggered animation for multiple elements
                        if (entry.target.classList.contains('post-card')) {
                            const delay = Array.from(document.querySelectorAll('.post-card')).indexOf(entry.target) * 100;
                            entry.target.style.animationDelay = delay + 'ms';
                        }
                    }
                });
            }, observerOptions);

            // Observe post cards and other elements
            document.querySelectorAll('.post-card, .card, .alert').forEach(element => {
                observer.observe(element);
            });
        },

        // Quick "flick" interactions
        setupQuickFlickEffects: function() {
            // Add flick gestures for mobile
            let startY = 0;
            let startTime = 0;
            
            document.addEventListener('touchstart', function(e) {
                startY = e.touches[0].clientY;
                startTime = Date.now();
            }, { passive: true });
            
            document.addEventListener('touchend', function(e) {
                const endY = e.changedTouches[0].clientY;
                const endTime = Date.now();
                const distance = endY - startY;
                const time = endTime - startTime;
                const velocity = Math.abs(distance / time);
                
                // If it's a quick flick
                if (velocity > 0.5 && Math.abs(distance) > 50 && time < 300) {
                    this.createFlickFeedback(e.changedTouches[0].clientX, endY);
                }
            }.bind(this), { passive: true });
        },

        // Visual feedback for flick gestures
        createFlickFeedback: function(x, y) {
            const feedback = document.createElement('div');
            feedback.className = 'flick-gesture-feedback';
            feedback.innerHTML = '⚡';
            
            feedback.style.position = 'fixed';
            feedback.style.left = x + 'px';
            feedback.style.top = y + 'px';
            feedback.style.pointerEvents = 'none';
            feedback.style.zIndex = '9999';
            feedback.style.fontSize = '24px';
            feedback.style.color = '#FF6B6B';
            
            document.body.appendChild(feedback);
            
            feedback.animate([
                { 
                    transform: 'translate(-50%, -50%) scale(0) rotate(-180deg)',
                    opacity: 0
                },
                { 
                    transform: 'translate(-50%, -50%) scale(1.2) rotate(0deg)',
                    opacity: 1
                },
                { 
                    transform: 'translate(-50%, -50%) scale(0) rotate(180deg)',
                    opacity: 0
                }
            ], {
                duration: 500,
                easing: 'cubic-bezier(0.68, -0.55, 0.265, 1.55)'
            }).onfinish = () => feedback.remove();
        },

        // Utility function to add sparkle effects
        createSparkles: function(element) {
            const sparkles = ['✨', '⭐', '🌟', '💫', '⚡'];
            const rect = element.getBoundingClientRect();
            
            for (let i = 0; i < 3; i++) {
                setTimeout(() => {
                    const sparkle = document.createElement('span');
                    sparkle.innerHTML = sparkles[Math.floor(Math.random() * sparkles.length)];
                    sparkle.className = 'flick-sparkle';
                    
                    sparkle.style.position = 'fixed';
                    sparkle.style.left = rect.left + Math.random() * rect.width + 'px';
                    sparkle.style.top = rect.top + Math.random() * rect.height + 'px';
                    sparkle.style.pointerEvents = 'none';
                    sparkle.style.zIndex = '9999';
                    sparkle.style.fontSize = '12px';
                    
                    document.body.appendChild(sparkle);
                    
                    sparkle.animate([
                        { 
                            transform: 'scale(0) rotate(0deg)',
                            opacity: 1
                        },
                        { 
                            transform: 'scale(1) rotate(180deg)',
                            opacity: 0.8
                        },
                        { 
                            transform: 'scale(0) rotate(360deg)',
                            opacity: 0
                        }
                    ], {
                        duration: 1000,
                        easing: 'ease-out'
                    }).onfinish = () => sparkle.remove();
                }, i * 200);
            }
        }
    };

    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        .flick-scroll-reveal {
            animation: flickScrollReveal 0.6s ease-out forwards;
        }
        
        @keyframes flickScrollReveal {
            from {
                opacity: 0;
                transform: translateY(30px) scale(0.95);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }
        
        .flick-shimmer {
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            overflow: hidden;
            pointer-events: none;
        }
        
        .flick-shimmer-line {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            animation: flickShimmer 0.6s ease-out;
        }
        
        @keyframes flickShimmer {
            from { transform: translateX(-100%); }
            to { transform: translateX(100%); }
        }
        
        .flick-form-focused {
            transform: scale(1.02);
            transition: all 0.2s ease-out;
        }
        
        /* Magnetic effect enhancement */
        .post-card, .card {
            transition: transform 0.1s ease-out;
        }
        
        /* Enhanced navbar transition */
        .navbar {
            transition: transform 0.3s cubic-bezier(0.4, 0.0, 0.2, 1), 
                        backdrop-filter 0.3s ease;
        }
        
        /* Loading states for buttons */
        .btn.loading {
            position: relative;
            color: transparent !important;
        }
        
        .btn.loading::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 16px;
            height: 16px;
            border: 2px solid currentColor;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: flickSpin 0.8s linear infinite;
        }
        
        @keyframes flickSpin {
            to { transform: translate(-50%, -50%) rotate(360deg); }
        }
    `;
    document.head.appendChild(style);

    // Initialize FLICK animations
    FlickAnimations.init();

    // Add global click feedback
    document.addEventListener('click', function(e) {
        if (e.target.matches('button, .btn, a, .action-btn')) {
            const ripple = document.createElement('span');
            ripple.className = 'flick-click-ripple';
            
            const rect = e.target.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                border-radius: 50%;
                background: rgba(255, 107, 107, 0.3);
                pointer-events: none;
                transform: scale(0);
                animation: flickRipple 0.6s ease-out;
            `;
            
            if (e.target.style.position !== 'absolute' && e.target.style.position !== 'relative') {
                e.target.style.position = 'relative';
            }
            e.target.style.overflow = 'hidden';
            e.target.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        }
    });

    // Add ripple animation CSS
    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
        @keyframes flickRipple {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(rippleStyle);
});

// Export for potential module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FlickAnimations;
}