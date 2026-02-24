from django.template.loader import render_to_string
from .session_messages import get_and_clear_messages

class JessMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Só injeta se for HTML e não for erro/redirecionamento crítico
        if "text/html" in response.get("Content-Type", "") and response.status_code == 200:
            messages = get_and_clear_messages(request)
            if messages:
                # Renderiza o Portal (A camada acima)
                portal_html = render_to_string('jessilver/messages_portal.html', {'messages': messages})
                
                # Injeção automática de CSS, JS e do HTML do Portal
                assets = (
                    f'<link rel="preconnect" href="https://fonts.googleapis.com">'
                    f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
                    f'<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">'
                    f'<link rel="stylesheet" href="/static/jessilver/css/jess-modal.css">'
                    f'{portal_html}'
                    f'<script src="/static/jessilver/js/jess-modal.js"></script>'
                )
                
                content = response.content.decode(response.charset)
                if "</body>" in content:
                    new_content = content.replace("</body>", f"{assets}</body>")
                    response.content = new_content.encode(response.charset)
                    response["Content-Length"] = len(response.content)
        return response