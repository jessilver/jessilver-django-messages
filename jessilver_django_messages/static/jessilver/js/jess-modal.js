const jessOrchestrator = {
    currentIndex: 0,
    frames: [],
    backdrop: null,
    container: null,
    _autoCloseTimer: null,

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

            // Inicia o timer de auto-close, se configurado
            const autoClose = currentFrame.dataset.autoClose;
            if (autoClose) {
                this._autoCloseTimer = setTimeout(
                    () => this.next(),
                    parseFloat(autoClose) * 1000
                );
            }
        } else {
            this.finish();
        }
    },

    next() {
        // Cancela o timer caso o usuário avance manualmente
        if (this._autoCloseTimer) {
            clearTimeout(this._autoCloseTimer);
            this._autoCloseTimer = null;
        }

        const currentFrame = this.frames[this.currentIndex];

        // Dispara animação de saída
        currentFrame.classList.add('jess-exit');

        // Aguarda a transição (250ms) antes de remover e avançar
        setTimeout(() => {
            currentFrame.remove();
            this.currentIndex++;
            this.renderCurrent();
        }, 250);
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