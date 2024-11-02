from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

class APIView(View):
    # Define the configuration at the class level
    pages_config = {
        'home': {'template': 'home.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
    }

    def get(self, request, page):
        # Get the page configuration
        page_config = self.pages_config.get(page)
        
        if not page_config:
            return JsonResponse({'html': "<p>404: NOT FOUND</p>"})

        # Check if the page requires authentication
        if page_config['auth_required'] and not request.user.is_authenticated:
            login_content = render(request, 'login.html').content.decode("utf-8")
            return JsonResponse({
                'html': login_content,
                'error': "You must be logged in to access this page."
            })

        # Render the requested page’s content
        html_content = render(request, page_config['template']).content.decode("utf-8")
        return JsonResponse({'html': html_content})