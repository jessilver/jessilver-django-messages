from django.utils.safestring import SafeString

def add_session_message(
    request,
    message_type='info',
    title=None,
    message='',
    extra_content=None,
    buttons=None,
    show_close_button=True,
    auto_close=None,
    **kwargs
):
    """
    Adiciona uma mensagem à pilha global da sessão.
    Garante que múltiplas chamadas na mesma view não se sobrescrevam.

    Estrutura de cada item em `buttons`:
        {
            'text': 'Confirmar',
            'class': 'jess-btn-success',   # classe CSS do botão
            'action': 'dismiss',            # 'dismiss' fecha o modal
            'callback': 'nomeDaFuncaoJS',   # opcional: função JS global
        }

    `auto_close` (int|float|None): segundos até o modal avançar
    automaticamente. None desativa o timer. Ideal para 'success' e
    'info'. Exemplos: auto_close=3, auto_close=5.
    """
    MASTER_KEY = 'jess_messages_stack'

    if MASTER_KEY not in request.session:
        request.session[MASTER_KEY] = []

    modal_data = {
        'type': message_type,
        'title': str(title) if title else 'Mensagem',
        'message': str(message),
        'extraContent': extra_content,
        'is_safe': isinstance(extra_content, SafeString) or isinstance(message, SafeString),
        'buttons': buttons or [],
        'show_close_button': show_close_button,
        'auto_close': auto_close,
    }

    request.session[MASTER_KEY].append(modal_data)
    request.session.modified = True


# ── Atalhos (Shortcuts) ───────────────────────────────────────

def add_success_message(request, message, title='Sucesso', auto_close=None):
    add_session_message(request, 'success', title, message, auto_close=auto_close)

def add_error_message(request, message, title='Erro', buttons=None):
    """
    Exibe uma mensagem de erro.

    `buttons` permite adicionar ações imediatas, como um botão
    "Tentar Novamente" que dispara um callback JS:

        add_error_message(
            request,
            'Falha ao salvar. Verifique sua conexão.',
            buttons=[
                {'text': 'Tentar Novamente', 'class': 'jess-btn-danger',
                 'action': 'dismiss', 'callback': 'onRetry'},
                {'text': 'Cancelar', 'class': 'jess-btn-secondary',
                 'action': 'dismiss', 'callback': ''},
            ]
        )
    """
    add_session_message(
        request=request,
        message_type='error',
        title=title,
        message=message,
        buttons=buttons,
    )

def add_warning_message(request, message, title='Aviso'):
    add_session_message(request, 'warning', title, message)

def add_info_message(request, message, title='Informação', auto_close=None):
    add_session_message(request, 'info', title, message, auto_close=auto_close)

def add_confirmation_message(
    request,
    message,
    title='Confirmação',
    confirm_text='Confirmar',
    cancel_text='Cancelar',
    confirm_callback=None,
):
    """
    Exibe um modal de confirmação com dois botões.

    `confirm_callback` é o nome de uma função JavaScript global
    que será chamada ao clicar em Confirmar.

    Exemplo:
        add_confirmation_message(
            request,
            'Tem certeza que deseja excluir este item?',
            title='Excluir item',
            confirm_callback='onConfirmDelete',
        )
    """
    buttons = [
        {
            'text': confirm_text,
            'class': 'jess-btn-success',
            'action': 'dismiss',
            'callback': confirm_callback or '',
        },
        {
            'text': cancel_text,
            'class': 'jess-btn-secondary',
            'action': 'dismiss',
            'callback': '',
        },
    ]
    add_session_message(
        request,
        message_type='warning',
        title=title,
        message=message,
        buttons=buttons,
        show_close_button=True,
    )


def get_and_clear_messages(request):
    """Recupera e limpa todas as mensagens da pilha."""
    return request.session.pop('jess_messages_stack', [])