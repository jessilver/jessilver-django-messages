# jessilver-django-messages

Mensagens modais sequenciais e seguras para Django — **esforço zero de implementação via Middleware**.

O sistema acumula mensagens em uma pilha na sessão e as exibe uma a uma em modais animados, injetados automaticamente antes do `</body>` de qualquer resposta HTML. Sem Bootstrap, sem jQuery.

---

## Instalação

```bash
pip install jessilver-django-messages
```

Ou em modo editável (desenvolvimento local):

```bash
pip install -e .
```

---

## Configuração

Adicione o app e o middleware ao `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'jessilver_django_messages',
]

MIDDLEWARE = [
    # ...
    'jessilver_django_messages.middleware.JessMessagesMiddleware',  # ao final
]
```

> O middleware deve ficar **após** os middlewares de sessão e autenticação do Django.

---

## Uso

### Mensagem simples

```python
from jessilver_django_messages.session_messages import (
    add_success_message,
    add_error_message,
    add_warning_message,
    add_info_message,
)

def minha_view(request):
    add_success_message(request, "Registro salvo com sucesso!")
    add_warning_message(request, "Atenção: o campo X está vazio.", title="Aviso")
    add_info_message(request, "Sua sessão expira em 10 minutos.")
    add_error_message(request, "Não foi possível conectar ao servidor.")
    return render(request, 'index.html')
```

### Mensagem de erro com botão "Tentar Novamente"

```python
from jessilver_django_messages.session_messages import add_error_message

def salvar(request):
    add_error_message(
        request,
        "Falha ao salvar. Verifique sua conexão.",
        title="Erro de Conexão",
        buttons=[
            {
                'text': 'Tentar Novamente',
                'class': 'jess-btn-danger',
                'action': 'dismiss',
                'callback': 'onRetry',   # função JS global
            },
            {
                'text': 'Cancelar',
                'class': 'jess-btn-secondary',
                'action': 'dismiss',
                'callback': '',
            },
        ]
    )
    return redirect('home')
```

```javascript
// No seu template ou arquivo JS global
function onRetry() {
    window.location.reload();
}
```

### Modal de Confirmação

A feature mais poderosa da lib. Exibe uma mensagem com dois botões e dispara um callback JavaScript ao confirmar.

```python
from jessilver_django_messages.session_messages import add_confirmation_message

def deletar_item(request, pk):
    add_confirmation_message(
        request,
        f"Tem certeza que deseja excluir o item #{pk}? Esta ação é irreversível.",
        title="Confirmar Exclusão",
        confirm_text="Sim, excluir",
        cancel_text="Cancelar",
        confirm_callback="onConfirmDelete",
    )
    return redirect('lista')
```

```javascript
function onConfirmDelete() {
    fetch('/deletar/confirmar/', { method: 'POST', headers: {'X-CSRFToken': getCookie('csrftoken')} })
        .then(() => window.location.reload());
}
```

### Conteúdo extra (formulários, HTML arbitrário)

```python
from django.utils.safestring import mark_safe
from jessilver_django_messages.session_messages import add_session_message

html = mark_safe('<input type="text" name="codigo" placeholder="Código de verificação">')

add_session_message(
    request,
    message_type='info',
    title='Verificação necessária',
    message='Insira o código enviado para seu e-mail:',
    extra_content=html,
)
```

> **Segurança:** Apenas `SafeString` / `mark_safe` é renderizado como HTML bruto.  
> Títulos e mensagens comuns são **sempre** escapados pelo Django.

---

## Funções disponíveis

| Função | Tipo | Descrição |
|---|---|---|
| `add_success_message(request, message, title)` | `success` | Operação concluída |
| `add_error_message(request, message, title, buttons)` | `error` | Falha ou erro |
| `add_warning_message(request, message, title)` | `warning` | Alerta ou aviso |
| `add_info_message(request, message, title)` | `info` | Informação neutra |
| `add_confirmation_message(request, message, title, confirm_text, cancel_text, confirm_callback)` | `warning` | Modal de confirmação com dois botões |
| `add_session_message(request, ...)` | qualquer | API completa com todos os parâmetros |

### Parâmetros de `add_session_message`

| Parâmetro | Tipo | Padrão | Descrição |
|---|---|---|---|
| `message_type` | `str` | `'info'` | `'success'`, `'error'`, `'warning'`, `'info'` |
| `title` | `str` | `'Mensagem'` | Título do modal |
| `message` | `str` | `''` | Corpo da mensagem |
| `extra_content` | `SafeString` | `None` | HTML adicional (requer `mark_safe`) |
| `buttons` | `list` | `[]` | Lista de botões customizados |
| `show_close_button` | `bool` | `True` | Exibe o botão `×` no header |

---

## Personalização visual

As cores são controladas por variáveis CSS no `:root` de `jess-modal.css`. Sobrescreva-as no CSS do seu projeto:

```css
:root {
    --jess-success:       #22c55e;
    --jess-success-dark:  #16a34a;
    --jess-success-light: #f0fdf4;

    --jess-error:         #ef4444;
    --jess-error-dark:    #dc2626;
    --jess-error-light:   #fff5f5;

    --jess-warning:       #f59e0b;
    --jess-warning-dark:  #d97706;
    --jess-warning-light: #fffbeb;

    --jess-info:          #3b82f6;
    --jess-info-dark:     #2563eb;
    --jess-info-light:    #eff6ff;

    --jess-radius: 1rem;   /* border-radius do card */
    --jess-font: 'Inter', system-ui, sans-serif;
}
```

---

## Testes

```bash
python manage.py test jessilver_django_messages
```

18 testes cobrindo: stacking, limpeza de sessão, tipos de mensagem, confirmação, botões, `show_close_button` e robustez do middleware (streaming, JSON, HTML, sessão vazia).

---

## Arquitetura

```
session_messages.py   →  pilha na sessão (jess_messages_stack)
        ↓
JessMessagesMiddleware →  render_to_string(messages_portal.html)
        ↓                 injetado antes de </body>
jess-modal.js         →  orquestrador sequencial (um modal por vez)
jess-modal.css        →  variáveis CSS + seletores :has() + animações
```

**Segurança:**
- Títulos e mensagens: escape nativo do Django Templates
- `extraContent`: apenas `SafeString` renderiza HTML bruto
- CSRF em formulários injetados: funciona nativamente via `render_to_string`
- Streaming / respostas não-HTML: middleware ignora sem efeito colateral

---

## Licença

MIT
