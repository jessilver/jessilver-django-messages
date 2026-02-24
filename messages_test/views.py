from django.shortcuts import render
from django.utils.safestring import mark_safe
from jessilver_django_messages.session_messages import (
    add_success_message,
    add_error_message,
    add_warning_message,
    add_info_message,
    add_confirmation_message,
)


def test_view(request):
    add_success_message(request, "Funcionou! Este é o card básico.", title="Sucesso Total", auto_close=3)
    add_error_message(request, "Funcionou! Este é o card básico.", title="Erro Total")
    add_warning_message(request, "Funcionou! Este é o card básico.", title="Aviso Total")
    add_info_message(request, "Funcionou! Este é o card básico.", title="Informação Total", auto_close=4)
    add_confirmation_message(request, "Funcionou! Este é o card básico.", title="Confirmação Total")
    return render(request, 'index.html')


def visual_stress_test_view(request):
    # 1. Mensagem simples — valida o fluxo básico (auto_close: fecha automático após 3s)
    add_success_message(
        request,
        "O motor de mensagens está operando corretamente!",
        title="Teste de Conexão",
        auto_close=3,
    )

    # 2. Informação com tabela — valida extra_content com HTML de tabela
    tabela_html = mark_safe("""
        <div class="table-responsive">
            <table class="table table-sm table-hover border mt-2">
                <thead class="table-light">
                    <tr><th>Aluno</th><th>Graduação</th><th>Status</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Jessé</td>
                        <td>Faixa Azul</td>
                        <td><span class="jess-text-success">✔ Ativo</span></td>
                    </tr>
                    <tr>
                        <td>Mari</td>
                        <td>Faixa Branca</td>
                        <td><span class="jess-text-warning">⚠ Pendente</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
    """)
    add_info_message(
        request,
        "Resumo da turma de Taekwondo:",
        title="Relatório de Alunos",
    )
    # injeta tabela via add_session_message para incluir extra_content
    from jessilver_django_messages.session_messages import add_session_message
    # sobrescreve a última mensagem adicionando extra_content
    # (re-adiciona como info com tabela)
    request.session['jess_messages_stack'][-1]['extraContent'] = tabela_html
    request.session.modified = True

    # 3. Aviso com formulário de upload — valida multipart + enctype
    form_html = mark_safe("""
        <form action="#" method="post" enctype="multipart/form-data"
              class="border p-3 rounded mt-2" style="background:#f8fafc">
            <label style="font-weight:600; display:block; margin-bottom:.5rem;">
                Atualizar Foto de Perfil:
            </label>
            <div style="display:flex; align-items:center; gap:1rem; margin-bottom:.75rem;">
                <img id="jess-foto-preview"
                     src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Ccircle cx='30' cy='30' r='30' fill='%23e5e7eb'/%3E%3Ccircle cx='30' cy='23' r='10' fill='%239ca3af'/%3E%3Cellipse cx='30' cy='48' rx='16' ry='10' fill='%239ca3af'/%3E%3C/svg%3E"
                     style="width:60px; height:60px; min-width:60px; min-height:60px;
                            border-radius:50%; border:2px solid #e5e7eb;
                            object-fit:cover; flex-shrink:0;"
                     alt="preview">
                <input type="file" name="foto"
                       style="font-size:.875rem; flex:1;"
                       accept="image/jpeg,image/png,image/webp"
                       onchange="(function(input){
                           var file = input.files[0];
                           if (!file) return;
                           var reader = new FileReader();
                           reader.onload = function(e) {
                               document.getElementById('jess-foto-preview').src = e.target.result;
                           };
                           reader.readAsDataURL(file);
                       })(this)">
            </div>
            <div style="font-size:.8rem; background:#eff6ff; border:1px solid #bfdbfe;
                        border-radius:.4rem; padding:.4rem .75rem; color:#1d4ed8;">
                Formatos aceitos: JPG, PNG e WebP.
            </div>
        </form>
    """)
    add_warning_message(
        request,
        "Detectamos que sua foto está desatualizada.",
        title="Ação Requerida",
    )
    request.session['jess_messages_stack'][-1]['extraContent'] = form_html
    request.session.modified = True

    # 4. Confirmação final com callback JS
    add_confirmation_message(
        request,
        "Deseja finalizar o teste visual e limpar a pilha de mensagens?",
        title="Finalizar Teste",
        confirm_text="Sim, finalizar",
        cancel_text="Cancelar",
        confirm_callback="onStressTestFinish",
    )

    return render(request, 'index.html')


def integration_test_view(request):
    """Testa coexistência com Bootstrap 5: o modal deve manter seu visual
    original mesmo com o Preflight/reset do Bootstrap na página."""

    # 1. Modal puro — baseline sem extra_content (auto_close: fecha após 4s)
    add_info_message(
        request,
        "O Bootstrap está carregado na página. Este modal deve manter fonte, cores e sombra originais.",
        title="Teste de Isolamento de Estilo",
        auto_close=4,
    )

    # 2. Modal com componentes Bootstrap dentro do extraContent
    #    Prova que o desenvolvedor pode usar o framework dele livremente
    extra_bootstrap = mark_safe("""
        <div class="alert alert-danger mt-2 py-2" role="alert">
            🚨 Sou um <strong>alert</strong> do Bootstrap dentro do JessModal!
        </div>
        <div class="d-flex gap-2 mt-2">
            <span class="badge bg-primary">Badge Primary</span>
            <span class="badge bg-success">Badge Success</span>
            <span class="badge bg-warning text-dark">Badge Warning</span>
        </div>
        <div class="progress mt-3" style="height: 8px;">
            <div class="progress-bar bg-info" style="width: 65%"></div>
        </div>
        <p class="text-muted mt-2" style="font-size:.8rem;">Progresso: 65%</p>
    """)
    add_warning_message(
        request,
        "Componentes Bootstrap renderizados dentro do extraContent:",
        title="Integração Confirmada",
    )
    request.session['jess_messages_stack'][-1]['extraContent'] = extra_bootstrap
    request.session.modified = True

    return render(request, 'index.html')