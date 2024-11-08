from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from srcs.user.models import CustomUser as User

class BaseSSRView(View):
    """
    A base Server Side Rendering view that serves different pages as JSON responses,
    with optional authentication requirements.

    Attributes:
        pages_config (dict): Configuration for each page, specifying the template
            to render and whether authentication is required.
        page (str): The identifier for the specific page to render.
    """

    pages_config = {
        'home': {'template': 'home.html', 'auth_required': False},
        'scoreboard': {'template': 'scoreboard.html', 'auth_required': False},
        'profile': {'template': 'profile.html', 'auth_required': True},
        'community': {'template': 'community.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
        'register': {'template': 'register.html', 'auth_required': False},
        'websocket': {'template': 'websocket.html', 'auth_required': True},
    }

    page = None
    error_message = None
    success_message = None
    context = None
    user = None
    all_users = None

    def get(self, request):
        """
        Handles GET requests and returns the content of the requested page
        as a JSON response. If the page requires authentication, checks the
        user's login status and redirects to the login page if unauthenticated.

        Parameters:
            request (HttpRequest): The HTTP request object.

        Returns:
            JsonResponse: Contains the HTML content of the page, or an error message
                if the page is not found or if the user is not authenticated.
        """
    
        if not self.page or self.page not in self.pages_config:
            return JsonResponse({'html': "<p>404: NOT FOUND</p>"})

        page_config = self.pages_config[self.page]
        
        self.context = {
            'error_message': self.error_message,
            'success_message': self.success_message,
            'user': self.user,
            'all_users': self.all_users,
        }

        # Check if the page requires authentication
        if page_config['auth_required'] and not request.user.is_authenticated:
            page_config = self.pages_config['login']
            self.context['error_message'] = 'You need to login to have access to this page.'
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")
            return JsonResponse({'html': html_content})
        else:
            html_content = render(request, page_config['template'], self.context).content.decode("utf-8")

        # print(html_content)  #* DEBUG
        return JsonResponse({'html': html_content})


class HomeView(BaseSSRView):
    """
    A view for the 'home' page.
    Inherits from BaseSSRView and sets the page attribute to 'home'.
    """

    page = 'home'


class WebSocketView(BaseSSRView):

    page = 'websocket'


class CommunityView(BaseSSRView):
    """
    A view for the 'community' page.
    Inherits from BaseSSRView and sets the page attribute to 'community'.
    """

    page = 'community'

    def get(self, request):
        self.all_users = User.objects.exclude(id=request.user.id)
        return super().get(request)


class ScoreboardView(BaseSSRView):
    """
    A view for the 'community' page.
    Inherits from BaseSSRView and sets the page attribute to 'community'.
    """

    page = 'scoreboard'

    def get(self, request):
        self.all_users = User.objects.all().order_by('-elo')
        return super().get(request)


class LoginView(BaseSSRView):
    """
    A view for the 'login' page.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """

    page = 'login'

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            self.success_message = 'Login successfull.'
            self.page = 'profile'
            self.user = request.user
            return super().get(request)
        else:
            self.error_message = 'Invalid username or password.'
            self.page = 'login'
            return super().get(request)


class LogoutView(BaseSSRView):
    """
    A view for 'logout'.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """
    
    page = 'login'

    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
            self.success_message = 'Logout successfull.'
        else:
            self.error_message = 'You are not authenticated.'
        return super().get(request)


class RegisterView(BaseSSRView):
    """
    A view for the 'register' page.
    Inherits from BaseSSRView and sets the page attribute to 'register'.
    """

    page = 'register'

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if User.objects.filter(username=username).exists():
            self.error_message = 'Username already exists.'
            return super().get(request)

        if User.objects.filter(email=email).exists():
            self.error_message = 'Email already in use.'
            return super().get(request)

        if password != confirm_password:
            self.error_message = 'Passwords do not match.'
            return super().get(request)

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            self.success_message = 'Registration successful. You are now logged in.'
            self.page = 'profile'
            self.user = request.user
            return super().get(request)
        except Exception as e:
            self.error_message = f"An error occurred: {str(e)}"
            return super().get(request)


class ProfileView(BaseSSRView):
    """
    A view for the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'profile'

    def get(self, request):
        #? /profile/?profile=exemple
        profile = request.GET.get('profile')
        # print("profile:", profile) #* Debug
        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        self.user = user
        return super().get(request)
    
    def post(self, request):
        profile = request.POST.get('profile')
        action = request.POST.get('action')
        type = request.POST.get('type')
        print("profile:", profile) #* Debug
        print("action:", action) #* Debug
        print("type:", type) #* Debug
        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        self.user = user
        return super().get(request)