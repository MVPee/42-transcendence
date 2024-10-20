from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from srcs.user.models import CustomUser as User
from django.db.models import Q #OR condition
from django.contrib import messages
from .models import Friend, Blocked, Message


@login_required
def index_view(request):
    # Pending friend requests received
    pending_received_requests = Friend.objects.filter(user2=request.user, status=False)

    # Accepted friendships
    accepted_friendships = Friend.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        status=True
    )

    # Blocked users
    blocked_users = Blocked.objects.filter(user1=request.user)

    # Handle search
    query = request.GET.get('search', '')  # Get the search query from the URL
    if query:
        all_users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
    else:
        all_users = User.objects.exclude(id=request.user.id)

    context = {
        'pending_received_requests': pending_received_requests,
        'accepted_friendships': accepted_friendships,
        'blocked_users': blocked_users,
        'all_users': all_users,
        'query': query  # Pass the query back to the template
    }
    return render(request, 'chat/index.html', context)


@login_required
def global_chat_view(request):
    return render(request, 'chat/global.html')


@login_required
def send_friend_request(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        if username:
            try:
                recipient = User.objects.get(username=username)
                if recipient == request.user:
                    messages.error(request, "You cannot send a friend request to yourself.")
                    return redirect('chat:index')

                # Check if a Friend relationship already exists
                friendship_exists = Friend.objects.filter(
                    Q(user1=request.user, user2=recipient) | 
                    Q(user1=recipient, user2=request.user)
                ).exists()

                if friendship_exists:
                    messages.error(request, "You are already friends or a friend request is pending.")
                    return redirect('chat:index')

                # Check if the recipient has blocked the sender or vice versa
                if Blocked.objects.filter(user1=request.user, user2=recipient).exists():
                    messages.error(request, "You have blocked this user and cannot send friend requests.")
                    return redirect('chat:index')
                if Blocked.objects.filter(user1=recipient, user2=request.user).exists():
                    messages.error(request, "You are blocked by this user and cannot send friend requests.")
                    return redirect('chat:index')

                # Create a new Friend request
                Friend.objects.create(user1=request.user, user2=recipient, status=False)
                messages.success(request, f"Friend request sent to {recipient.username}.")
                return redirect('chat:index')
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
                return redirect('chat:index')
        else:
            messages.error(request, "Please enter a username.")
            return redirect('chat:index')
    else:
        return redirect('chat:index')

@login_required
def send_friend_request_by_id(request, user_id):
    # Fetch the recipient by user_id
    recipient = get_object_or_404(User, id=user_id)
    
    if recipient == request.user:
        messages.error(request, "You cannot send a friend request to yourself.")
        return redirect('/profile/')

    # Check if a Friend relationship already exists
    friendship_exists = Friend.objects.filter(
        Q(user1=request.user, user2=recipient) | 
        Q(user1=recipient, user2=request.user)
    ).exists()

    if friendship_exists:
        messages.error(request, "You are already friends or a friend request is pending.")
        return redirect('/profile/' + recipient.username)

    # Check if the recipient has blocked the sender or vice versa
    if Blocked.objects.filter(user1=request.user, user2=recipient).exists():
        messages.error(request, "You have blocked this user and cannot send friend requests.")
        return redirect('/profile/' + recipient.username)

    if Blocked.objects.filter(user1=recipient, user2=request.user).exists():
        messages.error(request, "You are blocked by this user and cannot send friend requests.")
        return redirect('/profile/' + recipient.username)

    # Create a new Friend request
    Friend.objects.create(user1=request.user, user2=recipient, status=False)
    messages.success(request, f"Friend request sent to {recipient.username}.")
    
    return redirect('/profile/' + recipient.username)


@login_required
def respond_friend_request(request, friend_request_id):
    if request.method == 'POST':
        action = request.POST.get('action')
        friend_request = get_object_or_404(Friend, id=friend_request_id, user2=request.user, status=False)
        if action == 'accept':
            friend_request.status = True
            friend_request.save()
            messages.success(request, f"You are now friends with {friend_request.user1.username}.")
        elif action == 'decline':
            friend_request.delete()
            messages.success(request, f"You have declined the friend request from {friend_request.user1.username}.")
        else:
            messages.error(request, "Invalid action.")
    return redirect('chat:index')

@login_required
def unfriend(request, friendship_id):
    if request.method == 'POST':
        friendship = get_object_or_404(Friend, id=friendship_id, status=True)
        # Check if the current user is part of this friendship
        if friendship.user1 == request.user or friendship.user2 == request.user:
            # Identify the friend
            friend = friendship.user2 if friendship.user1 == request.user else friendship.user1
            friendship.delete()
            messages.success(request, f"You have unfriended {friend.username}.")
        else:
            messages.error(request, "You are not authorized to perform this action.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('chat:index')


@login_required
def block(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        if username:
            try:
                user_to_block = User.objects.get(username=username)
                if user_to_block == request.user:
                    messages.error(request, "You cannot block yourself.")
                elif Blocked.objects.filter(user1=request.user, user2=user_to_block).exists():
                    messages.error(request, f"You have already blocked {username}.")
                else:
                    # Remove any existing Friend relationships
                    Friend.objects.filter(
                        Q(user1=request.user, user2=user_to_block) | 
                        Q(user1=user_to_block, user2=request.user)
                    ).delete()
                    
                    # Create a new Blocked relationship
                    Blocked.objects.create(user1=request.user, user2=user_to_block)
                    messages.success(request, f"You have blocked {username}.")
            except User.DoesNotExist:
                messages.error(request, "User does not exist.")
        else:
            messages.error(request, "Please enter a username.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('profile/' + user_to_block.username)

@login_required
def block_by_id(request, user_id):
    # Retrieve the user to be blocked
    user_to_block = get_object_or_404(User, id=user_id)
    
    # Prevent blocking oneself
    if user_to_block == request.user:
        messages.error(request, "You cannot block yourself.")
    elif Blocked.objects.filter(user1=request.user, user2=user_to_block).exists():
        messages.error(request, f"You have already blocked {user_to_block.username}.")
    else:
        # Remove any existing Friend relationships
        Friend.objects.filter(
            Q(user1=request.user, user2=user_to_block) | 
            Q(user1=user_to_block, user2=request.user)
        ).delete()
        
        # Create a new Blocked relationship
        Blocked.objects.create(user1=request.user, user2=user_to_block)
        messages.success(request, f"You have blocked {user_to_block.username}.")

    # Redirect after the action
    return redirect('/profile/' + user_to_block.username)

@login_required
def unblock(request, blocked_id):
    if request.method == 'POST':
        blocked_relation = get_object_or_404(Blocked, id=blocked_id, user1=request.user)
        blocked_relation.delete()
        messages.success(request, f"You have unblocked {blocked_relation.user2.username}.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('/profile/' + blocked_relation.user2.username)


@login_required
def private_chat(request, friendship_id):
    user = request.user
    # Get the friendship instance
    friendship = get_object_or_404(Friend, id=friendship_id)

    # Check if the user is part of this friendship
    if friendship.user1 != user and friendship.user2 != user:
        messages.error(request, "You are not part of this chat.")
        return redirect('chat:index')

    # Determine the friend (the other user)
    if friendship.user1 == user:
        friend = friendship.user2
    else:
        friend = friendship.user1

    # Get previous chat messages
    chat_messages = Message.objects.filter(
        Q(sender=user, receiver=friend) | Q(sender=friend, receiver=user)
    ).order_by('created_at')

    context = {
        'user': user,
        'friend': friend,
        'friendship': friendship,
        'messages': chat_messages,
    }

    return render(request, 'chat/private_chat.html', context)