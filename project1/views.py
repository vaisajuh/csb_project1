from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from . models import Messages
import sqlite3
from django.utils.safestring import mark_safe

def login_view(request):
    create_tables()
    return render(request, 'project1/login.html')

def validate_view(request): 
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'project1/main.html')
    else:
        return render(request, 'project1/main.html')

def todo_view(request): # CSRF
    if request.user.id == None:
        return render(request, 'project1/main.html', {'todo': "Access denied!"})
    message = request.GET['message'] # should be POST
    if validate_length(message) == False:
        return render(request, 'project1/main.html', {'todo': "Input must be betweed 3 and 40"})
    Messages.objects.create(user=request.user, message=message)
    get_messages = Messages.objects.filter(user=request.user)
    return render(request, 'project1/main.html', {'messages': get_messages})


def register_bird_view(request): #broken authentication
    #if request.user.id == None:
        #return render(request, 'project1/main.html', {'register': "Access denied!"})
    bird = request.POST['bird']
    if validate_length(bird) == False:
        return render(request, 'project1/main.html', {'register': "Input must be between 3 and 40"})
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("INSERT INTO Birds (user_id, bird) VALUES (?, ?)", [request.user.id, bird])
    conn.commit()
    message = "Success!"
    return render(request, 'project1/main.html', {'message': message})

def get_bird_view(request): #injection and security misconfiguration
    if request.user.id == None:
        return render(request, 'project1/main.html', {'get': "Access denied!"})
    bird = request.POST['bird']
    bird = "%" + bird + "%"
    conn = sqlite3.connect('db.sqlite3')
    select_birds = conn.execute("SELECT bird FROM Birds WHERE user_id= %s "\
    "AND bird LIKE '%%%s%%'"% (request.user.id, bird)) #injection
    #select_birds = conn.execute("SELECT bird FROM Birds WHERE user_id=? AND bird like ?", [request.user.id, bird]) #correct
    birds = []
    for i in select_birds:
        birds.append(''.join(i))
    return render(request, 'project1/main.html', {'birds': birds})

def forum_view(request): #xss
    message = request.POST['message']
    if validate_length(message) == False:
        return render(request, 'project1/main.html', {'forum1': "Input must be between 3 and 40"})
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("INSERT INTO Forum (message) VALUES (?)", [message])
    conn.commit()
    messages = get_messages()
    return render(request, 'project1/main.html', {'forum': messages})

def get_messages():
    conn = sqlite3.connect('db.sqlite3')
    get_messages = conn.execute("SELECT message FROM Forum")
    messages = []
    for i in get_messages:
        messages.append(mark_safe(''.join(i))) #should not be marked as safe
    return messages


def validate_length(input):
    if len(input) in range(3, 40):
        return True
    return False

def create_tables():
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("CREATE TABLE IF NOT EXISTS Birds (id INTEGER PRIMARY KEY, user_id INTEGER, bird TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS Forum (id INTEGER PRIMARY KEY, message TEXT)")


def logout_view(request):
    logout(request)
    return render(request, 'project1/login.html')
