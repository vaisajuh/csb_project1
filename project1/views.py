import sqlite3
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User
from . models import Messages



def login_view(request):
    create_tables()
    create_users()
    return render(request, 'project1/login.html')

def validate_view(request): # Security logging and monitoring failures
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    #conn = sqlite3.connect('db.sqlite3')
    if user is not None:
        #hash = hashlib.md5(password.encode())
        #md5 = hash.hexdigest()
        #conn.execute("INSERT INTO Valid_logins (username, password) VALUES (?,?)", [username, md5])
        #conn.commit()
        login(request, user)
        return render(request, 'project1/main.html')
    else:
        #conn.execute("INSERT INTO Invalid_logins (username, password) VALUES (?,?)",
        #  [username, password])
        #conn.commit()
        return render(request, 'project1/login.html', {'invalid': "Access denied!"})

def todo_view(request): # CSRF and broken access control
    if request.user.username == "anonymous":
        return render(request, 'project1/main.html', {'todo': "Access denied!"})
    message = request.GET['message'] # Should be POST
    if validate_length(message) == False:
        return render(request, 'project1/main.html', {'todo': "Input must be betweed 3 and 40"})
    Messages.objects.create(user=request.user, message=message)
    get_messages = Messages.objects.filter(user=request.user)
    return render(request, 'project1/main.html', {'messages': get_messages})

def register_bird_view(request): # Broken access control
    # if request.user.id == anonymous:
        # return render(request, 'project1/main.html', {'register': "Access denied!"})
    bird = request.POST['bird']
    if validate_length(bird) == False:
        return render(request, 'project1/main.html', {'register': "Input must be between 3 and 40"})
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("INSERT INTO Birds (user_id, bird) VALUES (?, ?)", [request.user.id, bird])
    conn.commit()
    message = "Success!"
    return render(request, 'project1/main.html', {'message': message})

def get_bird_view(request): # Injection and security misconfiguration
    if request.user.username == "anonymous":
        return render(request, 'project1/main.html', {'get': "Access denied!"})
    bird = request.POST['bird']
    # bird = "%" + bird + "%"
    conn = sqlite3.connect('db.sqlite3')
    #try:
    select_birds = conn.execute("SELECT b.bird FROM Birds b JOIN auth_user a ON b.user_id = a.id"\
        " WHERE b.user_id= %s AND bird LIKE '%%%s%%'"% (request.user.id, bird)) #injection
    # select_birds = conn.execute("SELECT bird FROM Birds WHERE user_id=? AND bird like ?",
    #  [request.user.id, bird]) correct
    #catch:
        #pass
    birds = []
    for i in select_birds:
        birds.append(''.join(i))
    return render(request, 'project1/main.html', {'birds': birds})

def forum_view(request): # Xss
    message = request.POST['message']
    if validate_length(message) == False:
        return render(request, 'project1/main.html', {'forum1': "Input must be between 3 and 40"})
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("INSERT INTO Forum (user_id, message) VALUES (?,?)", [request.user.id, message])
    conn.commit()
    messages = get_messages()
    return render(request, 'project1/main.html', {'forum': messages})

def get_messages():
    conn = sqlite3.connect('db.sqlite3')
    get_messages = conn.execute("SELECT message FROM Forum ").fetchall()
    print(get_messages)
    messages = []
    for i in get_messages:
        messages.append(mark_safe(i[0])) # Should not be marked as safe
    return messages

def validate_length(entry):
    if len(entry) in range(3, 40):
        return True
    return False

def create_tables():
    conn = sqlite3.connect('db.sqlite3')
    conn.execute("CREATE TABLE IF NOT EXISTS Birds "\
    " (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES auth_user, bird TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS Forum"\
    " (id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES auth_user, message TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS Invalid_logins"\
    " (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS Valid_logins"\
    " (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")

def create_users():
    try:
        User.objects.create_user('george', 'carelesswhisper')
        User.objects.create_user('jormao', 'nokia5110')
        User.objects.create_user('anonymous', 'anonymous')
    except:
        pass

def logout_view(request):
    logout(request)
    return render(request, 'project1/login.html')
