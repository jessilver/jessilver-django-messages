const jessOrchestrator = {
    currentIndex: 0,
    frames: [],
    backdrop: null,
    container: null,

    init() {
        this.frames = document.querySelectorAll('.jess-frame');
        this.backdrop = document.getElementById('jess-portal-backdrop');
        this.container = document.getElementById('jess-active-frame-container');
        
        if (this.frames.length > 0) this.start();
    },

    start() {
        this.backdrop.style.display = 'flex';
        // Pequeno delay para a opacidade do backdrop animar
        setTimeout(() => this.backdrop.classList.add('jess-show'), 10);
        this.renderCurrent();
    },

    renderCurrent() {
        if (this.currentIndex < this.frames.length) {
            const currentFrame = this.frames[this.currentIndex];
            this.container.appendChild(currentFrame);
            currentFrame.style.display = 'flex';
        } else {
            this.finish();
        }
    },

    next() {
        const currentFrame = this.frames[this.currentIndex];
        // Remove animação e limpa
        currentFrame.remove();
        this.currentIndex++;
        this.renderCurrent();
    },

    handleAction(action, callback) {
        if (action === 'dismiss') this.next();
        if (callback && typeof window[callback] === 'function') {
            window[callback]();
        }
    },

    finish() {
        this.backdrop.classList.remove('jess-show');
        setTimeout(() => {
            this.backdrop.style.display = 'none';
        }, 300);
    }
};

document.addEventListener('DOMContentLoaded', () => jessOrchestrator.init());