from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from srcs.user.models import CustomUser as User
from srcs.community.models import Blocked, Friend
from srcs.game.models import Match
from django.db.models import Q

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
        'settings': {'template': 'settings.html', 'auth_required': True},
        'community': {'template': 'community.html', 'auth_required': True},
        'login': {'template': 'login.html', 'auth_required': False},
        'register': {'template': 'register.html', 'auth_required': False},
        'chat': {'template': 'chat.html', 'auth_required': True},
    }

    context = None
    page = None

    error_message = None
    success_message = None

    user = None
    all_users = None

    friend = None
    friend_request = None
    blocked = None

    matchs = None
    winrate = None
    average_score = None

    def get(self, request, *args, **kwargs):
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
            'friend': self.friend,
            'friend_request': self.friend_request,
            'blocked': self.blocked,
            'matchs': self.matchs,
            'winrate': self.winrate,
            'average_score': self.average_score,
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


class ChatView(BaseSSRView):
    """
    A view for the 'chat' page.
    Inherits from BaseSSRView and sets the page attribute to 'chat'.
    """

    page = 'chat'

    def get(self, request, *args, **kwargs):

        id = kwargs.get('id')
        friend = Friend.objects.filter((Q(user1=request.user.id) | Q(user2=request.user.id)), status=True).first()
        if (friend is None or friend.id != id):
            self.page = 'community'
            self.error_message = 'You can\'t access to this page'
            self.all_users = User.objects.exclude(id=request.user.id)
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

        friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id)).first()
        blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()
        self.friend = friend if friend and friend.status else None
        self.friend_request = friend and (friend.user1 == request.user or friend.status)
        self.blocked = blocked
        self.user = user
        self.matchs = Match.objects.filter(Q(user1=user) | Q(user2=user)).order_by('-created_at')

        total_matches = self.matchs.count()
        wins = sum(1 for match in self.matchs if (match.user1 == user and match.user1_score > match.user2_score) or 
                   (match.user2 == user and match.user2_score > match.user1_score))
        self.average_score = round((sum(match.user1_score for match in self.matchs if match.user1 == user) + 
                            sum(match.user2_score for match in self.matchs if match.user2 == user)) / total_matches, 2) if total_matches > 0 else 0
        self.winrate = round((wins / total_matches * 100), 2) if total_matches > 0 else 0

        return super().get(request)


class SettingsView(BaseSSRView):
    """
    A view for the 'settings' page.
    Inherits from BaseSSRView and sets the page attribute to 'settings'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'settings'

    def get(self, request):
        self.user = request.user
        return super().get(request)


class LogoutRequest(BaseSSRView):
    """
    A view for 'logout'.
    Inherits from BaseSSRView and sets the page attribute to 'login'.
    """
    
    page = 'login'

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
            self.success_message = 'Logout successfull.'
        else:
            self.error_message = 'You are not authenticated.'
        return super().get(request)


class SettingsRequest(BaseSSRView):
    """
    A view for the 'settings' page.
    Inherits from BaseSSRView and sets the page attribute to 'settings'.
    
    Methods:
        get(request): Overrides the base get method to allow retrieving
            a profile parameter from the request's query string.
    """
    
    page = 'settings'

    def post(self, request):
        self.user = request.user
        action = request.POST.get('action')
        value = request.POST.get('value')

        if (action == 'username' and value):
            new_username = value
            if User.objects.filter(username=new_username).exclude(id=self.user.id).exists():
                self.error_message = 'Username already taken.'
            elif self.user.username == new_username:
                self.error_message = 'You need to use your keyboard to change your username.'
            else:
                self.user.username = new_username
                self.user.save()
                self.success_message = f'Username updated successfully to {new_username}'

        elif (action == 'email' and value):
            new_email = value
            if User.objects.filter(email=new_email).exclude(id=self.user.id).exists():
                self.error_message = 'Email already taken.'
            elif self.user.email == new_email:
                self.error_message = 'You need to use your keyboard to change your email.'
            else:
                self.user.email = new_email
                self.user.save()
                self.success_message = f'Email updated successfully to {new_email}'

        elif (action == 'language' and value):
            new_language = value
            if self.user.language == new_language:
                self.error_message = 'You need to use your mouse to change your language.'
            elif new_language in ['EN', 'FR', 'DE']:
                self.user.language = new_language
                self.user.save()
                self.success_message = 'Language updated successfully.'
            else:
                self.error_message = 'Invalid language selection.'

        return super().get(request)


class FriendRequest(BaseSSRView):
    """
    Handling friend requests on the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        post(request): Processes friend requests based on the profile, action, and type parameters in the request body.
    """

    page = 'profile'
    
    def post(self, request):
        profile = request.POST.get('profile')
        type = request.POST.get('type')
        print("FRIEND REQUEST") #* Debug
        print("profile:", profile) #* Debug
        print("type:", type) #* Debug

        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        else:
            friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id) ).first()

            if type=='add':
                if friend is None: #? Create a new friend with status pending
                    friend = Friend.objects.create(user1=request.user, user2=user, status=False)
                    friend.save()
                    self.success_message = f"Sucessfuly sent a friend request to {profile}."
                else:
                    if friend.status is True:
                        self.error_message = f"{profile} is already your friend."
                    elif friend.user1 == request.user: #? if initial friend request came from me
                         self.error_message = f"A friend request was already sent to {profile}."
                    else: #? if initial friend request did not came from me
                        self.success_message = f"You and {profile} are now friends !"
                        friend.status = True
                        friend.save()

                self.friend = friend.status
                self.friend_request = friend.user1 == request.user or friend.status

            elif type=='remove':
                if friend is None:
                    self.error_message = f"{profile} is not in your friend list."
                else:
                    if friend.user1 == request.user:  #? if initial friend request came from me
                        if friend.status is False:
                            self.success_message = f"{profile} friend request sucessfuly aborted."
                        else :
                            self.success_message = f"{profile} has been removed from your friends."
                    else:
                        if friend.status is False:
                            self.error_message = f"A friend request to {profile} was never sent."

                friend.delete()
                self.friend = False
                self.friend_request = False

            self.blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()

        self.user = user
        return super().get(request)


class BlockRequest(BaseSSRView):
    """
    Handling block requests on the 'profile' page.
    Inherits from BaseSSRView and sets the page attribute to 'profile'.
    
    Methods:
        post(request): Processes friend requests based on the profile, action, and type parameters in the request body.
    """

    page = 'profile'
    
    def post(self, request):
        profile = request.POST.get('profile')
        type = request.POST.get('type')
        print("BLOCK REQUEST") #* Debug
        print("profile:", profile) #* Debug
        print("type:", type) #* Debug
        user = User.objects.filter(username=profile).first()
        if user is None:
            user = request.user
        else:
            blocked = Blocked.objects.filter(user1=request.user.id, user2=user.id).first()

            if type=='add':
                if blocked is None: 
                    new_blocked = Blocked.objects.create(user1=request.user, user2=user)
                    new_blocked.save()
                    self.success_message = f"Sucessfuly blocked {profile}."
                else:
                    self.error_message = f"{profile} is already blocked."
                #? remove the friend relation in the database if they were friend
                friend = Friend.objects.filter(Q(user1=request.user.id, user2=user.id) | Q(user1=user.id, user2=request.user.id) ).first()
                if (friend):
                    friend.delete()
            elif type=='remove':
                if blocked is None: 
                    self.error_message = f"{profile} was not blocked."
                else:
                    blocked.delete()
                    self.success_message = f"{profile} is not blocked anymore."

            self.friend = False 
            self.friend_request = False
            self.blocked = type=='add'
        
        self.user = user
        return super().get(request)
