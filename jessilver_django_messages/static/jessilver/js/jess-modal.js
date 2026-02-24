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

        if (this.frames.length > 0) {
            // Tecla Escape: sacudir o modal atual (não fechar)
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') this.shake();
            });

            // Clique fora do dialog (no overlay): sacudir
            this.backdrop.addEventListener('click', (e) => {
                if (e.target === this.backdrop) this.shake();
            });

            this.start();
        }
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

            // Força reflow: garante que o browser registra o estado inicial
            // (scale(0.9) opacity:0) antes de disparar a transição de entrada.
            // Necessário para todos os modais, não apenas o primeiro.
            void currentFrame.offsetWidth;
            currentFrame.classList.add('jess-visible');

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

        // Aguarda a transição (220ms) antes de remover e avançar
        setTimeout(() => {
            currentFrame.remove();
            this.currentIndex++;
            this.renderCurrent();
        }, 220);
    },

    handleAction(action, callback) {
        if (action === 'dismiss') this.next();
        if (callback && typeof window[callback] === 'function') {
            window[callback]();
        }
    },

    shake() {
        const currentFrame = this.frames[this.currentIndex];
        // Não sacudir se não há modal visível ou se já está saindo
        if (!currentFrame || currentFrame.classList.contains('jess-exit')) return;

        // Reinicia a animação caso já esteja sacudindo (clique duplo)
        currentFrame.classList.remove('jess-shake');
        void currentFrame.offsetWidth;
        currentFrame.classList.add('jess-shake');

        currentFrame.addEventListener('animationend', () => {
            currentFrame.classList.remove('jess-shake');
        }, { once: true });
    },

    finish() {
        this.backdrop.classList.remove('jess-show');
        setTimeout(() => {
            this.backdrop.style.display = 'none';
        }, 300);
    }
};

document.addEventListener('DOMContentLoaded', () => jessOrchestrator.init());