from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import SignUpForm, UserLoginForm
from firebase_admin import firestore

def home(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Get the ID of the logged-in user
        user_id = request.user.id
        # Access Firestore database
        db = firestore.client()

        # Fetch data from Firestore
        users_ref = db.collection(u'users')
        users = users_ref.get()

        user_data = []
        for user in users:
            user_data.append(user.to_dict())

        context ={
            'user_id': user_id,
            'user_data': user_data
        }
        # You can now use user_id in your template or perform other actions
        return render(request, 'home.html', context=context)
    else:
        # Handle the case where the user is not authenticated
        # Redirect the user to the login page or display a message
        # return redirect('login')  # Assuming 'login' is the name of your login URL
        context ={
            'user_id': None,
            'user_data': None
        }
        # You can now use user_id in your template or perform other actions
        return render(request, 'home.html', context=context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user to Django database
            user = form.save()
            
            # Automatically log in the user after signup
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password1'])
            login(request, user)
            
            # Save the user's email to Firestore
            db = firestore.client()
            users_ref = db.collection(u'users')
            users_ref.document(str(user.id)).set({
                u'email': form.cleaned_data['email'],
                # Add other user information as needed
            })
            
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                # Authentication failed, handle error
                pass
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')
