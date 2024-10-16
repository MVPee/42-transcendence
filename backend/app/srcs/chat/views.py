from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from srcs.user.models import CustomUser as User
from django.db.models import Q #OR condition
from .models import Friend
from django.contrib import messages

@login_required
def index_view(request):
    # Pending friend requests received
    pending_received_requests = Friend.objects.filter(user2=request.user, status=False)

    # Pending friend requests sent
    pending_sent_requests = Friend.objects.filter(user1=request.user, status=False)

    # Accepted friendships
    accepted_friendships = Friend.objects.filter(
        (Q(user1=request.user) | Q(user2=request.user)),
        status=True
    )

    context = {
        'pending_received_requests': pending_received_requests,
        'pending_sent_requests': pending_sent_requests,
        'accepted_friendships': accepted_friendships
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
                    user1=request.user,
                    user2=recipient
                ).exists() or Friend.objects.filter(
                    user1=recipient,
                    user2=request.user
                ).exists()

                if friendship_exists:
                    messages.error(request, "You are already friends or a friend request is pending.")
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