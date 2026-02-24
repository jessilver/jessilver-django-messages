from jessilver_django_messages.session_messages import add_success_message, add_error_message, add_warning_message, add_info_message, add_confirmation_message
from django.shortcuts import render

def test_view(request):
    add_success_message(request, "Funcionou! Este é o card básico.", title="Sucesso Total")
    add_error_message(request, "Funcionou! Este é o card básico.", title="Erro Total")
    add_warning_message(request, "Funcionou! Este é o card básico.", title="Aviso Total")
    add_info_message(request, "Funcionou! Este é o card básico.", title="Informação Total")
    add_confirmation_message(request, "Funcionou! Este é o card básico.", title="Confirmação Total")
    return render(request, 'index.html')