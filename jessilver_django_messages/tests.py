from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.safestring import mark_safe
from django.middleware.csrf import get_token

from .session_messages import (
    add_success_message,
    add_error_message,
    add_warning_message,
    add_info_message,
    add_confirmation_message,
    add_session_message,
    get_and_clear_messages,
)
from .middleware import JessMessagesMiddleware


# ── Helpers de payload ────────────────────────────────────────────────────────

def get_complex_payload(request):
    """Gera um HTML extremamente denso para teste de carga.

    Combina: form multipart, token CSRF real, tabela de dados,
    ícones, badges e inputs de arquivo — espelhando conteúdos
    reais como fichas de matrícula e uploads de foto.
    """
    csrf_token = get_token(request)
    return mark_safe(f"""
        <div class="jess-stress-test">
            <header class="d-flex justify-content-between">
                <h4>Ficha de Matrícula #1234</h4>
                <span class="badge bg-primary">Pendente</span>
            </header>
            <table class="table table-striped my-3">
                <thead><tr><th>Documento</th><th>Status</th></tr></thead>
                <tbody>
                    <tr><td>RG Frente</td><td><i class="fas fa-check"></i></td></tr>
                    <tr><td>Foto de Corpo</td><td><i class="fas fa-times"></i></td></tr>
                </tbody>
            </table>
            <form action="/api/v1/upload/" method="post"
                  enctype="multipart/form-data" id="stressForm">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
                <div class="mb-3">
                    <label class="form-label">Selecione a nova foto:</label>
                    <input type="file" name="foto_corpo"
                           class="form-control" accept="image/*">
                </div>
                <div class="row g-2">
                    <div class="col-6">
                        <button type="button"
                                class="btn btn-outline-danger w-100">Cancelar</button>
                    </div>
                    <div class="col-6">
                        <button type="submit"
                                class="btn btn-success w-100">Enviar Foto</button>
                    </div>
                </div>
            </form>
        </div>
    """)


class MessageStackTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self):
        """Cria um request com sessão funcional."""
        request = self.factory.get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
        return request

    # ── Stacking ─────────────────────────────────────────────

    def test_message_stacking(self):
        """Múltiplas mensagens se acumulam na ordem correta."""
        request = self._make_request()
        add_success_message(request, "Mensagem 1")
        add_success_message(request, "Mensagem 2")

        stack = get_and_clear_messages(request)
        self.assertEqual(len(stack), 2)
        self.assertEqual(stack[0]['message'], "Mensagem 1")
        self.assertEqual(stack[1]['message'], "Mensagem 2")

    def test_session_clearing(self):
        """A pilha é limpa após o consumo."""
        request = self._make_request()
        add_success_message(request, "Teste")
        get_and_clear_messages(request)
        self.assertEqual(len(get_and_clear_messages(request)), 0)

    def test_empty_stack_returns_empty_list(self):
        """Consumir uma sessão sem mensagens retorna lista vazia."""
        request = self._make_request()
        self.assertEqual(get_and_clear_messages(request), [])

    # ── Tipos e campos ───────────────────────────────────────

    def test_message_type_fields(self):
        """Cada atalho define corretamente o campo 'type'."""
        request = self._make_request()
        add_success_message(request, "s")
        add_error_message(request, "e")
        add_warning_message(request, "w")
        add_info_message(request, "i")

        stack = get_and_clear_messages(request)
        types = [m['type'] for m in stack]
        self.assertEqual(types, ['success', 'error', 'warning', 'info'])

    def test_default_title_fallback(self):
        """Quando title=None, o título padrão é 'Mensagem'."""
        request = self._make_request()
        add_session_message(request, message_type='info', title=None, message='x')
        stack = get_and_clear_messages(request)
        self.assertEqual(stack[0]['title'], 'Mensagem')

    def test_mixed_stack(self):
        """Tipos diferentes se acumulam sem interferência."""
        request = self._make_request()
        add_success_message(request, "ok")
        add_error_message(request, "fail")
        stack = get_and_clear_messages(request)
        self.assertEqual(len(stack), 2)
        self.assertEqual(stack[0]['type'], 'success')
        self.assertEqual(stack[1]['type'], 'error')

    # ── Confirmação ──────────────────────────────────────────

    def test_confirmation_has_two_buttons(self):
        """add_confirmation_message gera exatamente 2 botões."""
        request = self._make_request()
        add_confirmation_message(request, "Tem certeza?")
        stack = get_and_clear_messages(request)
        self.assertEqual(len(stack[0]['buttons']), 2)

    def test_confirmation_button_texts(self):
        """Textos padrão dos botões de confirmação estão corretos."""
        request = self._make_request()
        add_confirmation_message(request, "Deletar?")
        buttons = get_and_clear_messages(request)[0]['buttons']
        texts = [b['text'] for b in buttons]
        self.assertIn('Confirmar', texts)
        self.assertIn('Cancelar', texts)

    def test_confirmation_custom_texts(self):
        """Textos customizados dos botões são respeitados."""
        request = self._make_request()
        add_confirmation_message(request, "Sair?", confirm_text="Sim", cancel_text="Não")
        buttons = get_and_clear_messages(request)[0]['buttons']
        texts = [b['text'] for b in buttons]
        self.assertIn('Sim', texts)
        self.assertIn('Não', texts)

    def test_confirmation_callback(self):
        """O callback JS é armazenado corretamente no botão de confirmar."""
        request = self._make_request()
        add_confirmation_message(request, "?", confirm_callback='onDelete')
        buttons = get_and_clear_messages(request)[0]['buttons']
        confirm_btn = buttons[0]
        self.assertEqual(confirm_btn['callback'], 'onDelete')

    # ── show_close_button ────────────────────────────────────

    def test_show_close_button_default_true(self):
        """show_close_button é True por padrão."""
        request = self._make_request()
        add_success_message(request, "x")
        stack = get_and_clear_messages(request)
        self.assertTrue(stack[0]['show_close_button'])

    def test_show_close_button_false(self):
        """show_close_button pode ser desativado."""
        request = self._make_request()
        add_session_message(request, message_type='info', message='x', show_close_button=False)
        stack = get_and_clear_messages(request)
        self.assertFalse(stack[0]['show_close_button'])

    # ── Auto-close ───────────────────────────────────────────

    def test_auto_close_stored_in_modal_data(self):
        """auto_close é armazenado corretamente no modal_data."""
        request = self._make_request()
        add_success_message(request, "Salvo!", auto_close=3)
        stack = get_and_clear_messages(request)
        self.assertEqual(stack[0]['auto_close'], 3)

    def test_auto_close_default_is_none(self):
        """auto_close é None por padrão (modal não fecha sozinho)."""
        request = self._make_request()
        add_success_message(request, "Sem timer")
        stack = get_and_clear_messages(request)
        self.assertIsNone(stack[0]['auto_close'])

    def test_auto_close_via_add_session_message(self):
        """add_session_message repassa auto_close para qualquer tipo."""
        request = self._make_request()
        add_session_message(request, message_type='warning', message='x', auto_close=5)
        stack = get_and_clear_messages(request)
        self.assertEqual(stack[0]['auto_close'], 5)

    def test_auto_close_rendered_in_html(self):
        """Middleware injeta data-auto-close no HTML quando auto_close está definido."""
        request = self._make_request()
        add_info_message(request, "Fechar logo", auto_close=2)
        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        result = mw(request)
        self.assertIn(b'data-auto-close="2"', result.content)

    def test_auto_close_absent_from_html_when_none(self):
        """data-auto-close não aparece no HTML quando auto_close=None."""
        request = self._make_request()
        add_info_message(request, "Sem timer")
        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        result = mw(request)
        self.assertNotIn(b'data-auto-close', result.content)

    def test_timer_bar_rendered_in_html(self):
        """Middleware injeta jess-timer-bar e animation-duration correto
        quando auto_close está definido."""
        request = self._make_request()
        add_info_message(request, "Fechar rápido", auto_close=2)
        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        result = mw(request)
        self.assertIn(b'jess-timer-bar', result.content)
        self.assertIn(b'animation-duration: 2s', result.content)

    def test_timer_bar_absent_when_no_auto_close(self):
        """jess-timer-bar não aparece no HTML quando auto_close=None."""
        request = self._make_request()
        add_info_message(request, "Sem timer")
        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        result = mw(request)
        self.assertNotIn(b'jess-timer-bar', result.content)


class ErrorMessageTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_error_message_without_buttons(self):
        """add_error_message sem botões gera lista vazia de botões."""
        request = self._make_request()
        add_error_message(request, "Algo falhou")
        stack = get_and_clear_messages(request)
        self.assertEqual(stack[0]['type'], 'error')
        self.assertEqual(stack[0]['buttons'], [])

    def test_error_message_with_buttons(self):
        """add_error_message aceita botões customizados."""
        request = self._make_request()
        buttons = [
            {'text': 'Tentar Novamente', 'class': 'jess-btn-danger',
             'action': 'dismiss', 'callback': 'onRetry'},
            {'text': 'Cancelar', 'class': 'jess-btn-secondary',
             'action': 'dismiss', 'callback': ''},
        ]
        add_error_message(request, "Falha na conexão", buttons=buttons)
        stack = get_and_clear_messages(request)
        self.assertEqual(len(stack[0]['buttons']), 2)
        self.assertEqual(stack[0]['buttons'][0]['callback'], 'onRetry')


class MiddlewareRobustnessTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def _make_middleware(self, response):
        return JessMessagesMiddleware(get_response=lambda r: response)

    def test_ignores_streaming_response(self):
        """Middleware não toca em StreamingHttpResponse."""
        request = self._make_request()
        add_success_message(request, "nunca injetado")
        streaming = StreamingHttpResponse(streaming_content=iter([b"chunk"]))
        mw = self._make_middleware(streaming)
        result = mw(request)
        self.assertIsInstance(result, StreamingHttpResponse)

    def test_ignores_non_html_response(self):
        """Middleware ignora respostas com Content-Type não-HTML (ex: JSON)."""
        request = self._make_request()
        add_success_message(request, "nunca injetado")
        json_response = HttpResponse('{"ok": true}', content_type='application/json')
        mw = self._make_middleware(json_response)
        result = mw(request)
        self.assertNotIn(b'jess-modal', result.content)

    def test_injects_into_html_response(self):
        """Middleware injeta o portal em respostas HTML com </body>."""
        request = self._make_request()
        add_success_message(request, "Funcionou")
        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = self._make_middleware(html_response)
        result = mw(request)
        self.assertIn(b'jess-modal', result.content)

    def test_no_injection_without_messages(self):
        """Middleware não altera a resposta se não houver mensagens na sessão."""
        request = self._make_request()
        original = '<html><body></body></html>'
        html_response = HttpResponse(original, content_type='text/html')
        mw = self._make_middleware(html_response)
        result = mw(request)
        self.assertEqual(result.content, original.encode())

    def test_extreme_extra_content_complexity(self):
        """HTML pesado (tabela + form + imagem + file input) sobrevive à
        serialização de sessão e à injeção do middleware sem corrupção."""
        from django.utils.safestring import mark_safe

        request = self._make_request()

        complex_html = mark_safe("""
            <div class="test-container">
                <h4>Resumo de Cadastro</h4>
                <table class="table jess-custom-table">
                    <thead><tr><th>Campo</th><th>Valor</th></tr></thead>
                    <tbody>
                        <tr><td>Status</td><td><span class="badge">Ativo</span></td></tr>
                    </tbody>
                </table>
                <form action="/upload/" method="post" enctype="multipart/form-data">
                    <input type="hidden" name="csrfmiddlewaretoken" value="dummy-token">
                    <div class="upload-area">
                        <img src="/static/img/preview.webp" alt="Preview">
                        <input type="file" name="foto" required>
                    </div>
                    <button type="submit">Enviar</button>
                </form>
            </div>
        """)

        add_session_message(
            request,
            message_type='warning',
            title='Complex Test',
            message='Teste de carga HTML',
            extra_content=complex_html,
        )

        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        result = mw(request)
        content = result.content.decode()

        # Integridade estrutural: todas as tags críticas devem estar presentes
        self.assertIn('<table class="table jess-custom-table">', content)
        self.assertIn('<form action="/upload/"', content)
        self.assertIn('<img src="/static/img/preview.webp"', content)
        self.assertIn('type="file"', content)

        # Segurança: mensagem e título escapados normalmente
        self.assertIn('Teste de carga HTML', content)
        self.assertIn('Complex Test', content)

        # Garante que o extra_content é marcado como safe (sem escape de tags)
        self.assertNotIn('&lt;table', content)
        self.assertNotIn('&lt;form', content)

    def test_middleware_complex_html_persistence(self):
        """HTML com CSRF real, tabela, multipart e file input sobrevive
        intacto à serialização de sessão e à injeção do middleware."""
        request = self._make_request()
        payload = get_complex_payload(request)

        add_session_message(
            request,
            message_type='warning',
            title='Carga Pesada',
            message='Verifique os dados abaixo',
            extra_content=payload,
        )

        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        response = mw(request)
        content = response.content.decode()

        self.assertIn('enctype="multipart/form-data"', content)   # suporte a arquivos
        self.assertIn('<table', content)                           # tabelas renderizadas
        self.assertIn('csrfmiddlewaretoken', content)             # CSRF preservado
        self.assertIn('jess-modal-content', content)              # container da lib presente
        self.assertIn('foto_corpo', content)                      # input de arquivo intacto
        self.assertIn('Ficha de Matrícula #1234', content)        # conteúdo textual intacto

    def test_xss_protection_in_complex_content(self):
        """message maliciosa é escapada; extra_content safe permanece íntegro."""
        request = self._make_request()
        malicious_msg = "<script>alert('xss')</script>"
        safe_extra = mark_safe("<div class='safe'>Conteúdo Seguro</div>")

        add_session_message(
            request,
            message_type='error',
            message=malicious_msg,
            extra_content=safe_extra,
        )

        html_response = HttpResponse('<html><body></body></html>', content_type='text/html')
        mw = JessMessagesMiddleware(get_response=lambda r: html_response)
        response = mw(request)
        content = response.content.decode()

        # message deve estar escapada — browser exibe texto, não executa script
        self.assertIn("&lt;script&gt;", content)
        self.assertNotIn("<script>alert('xss')</script>", content)

        # extra_content safe deve estar íntegro
        self.assertIn("<div class='safe'>Conteúdo Seguro</div>", content)
        self.assertNotIn("&lt;div class=&#x27;safe&#x27;&gt;", content)
