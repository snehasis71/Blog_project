from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout

#for highlighting search
import re
from django.utils.safestring import mark_safe

#for Search
from django.db.models import Q

from .models import Post
from .models import Comment
from mainapp.forms import PostForm

#Pagination
from django.core.paginator import Paginator

from django.contrib.auth.decorators import login_required

def paginate_queryset (request, queryset, per_page=5):
    paginator = Paginator (queryset, per_page)
    page_number = request.GET.get ('page')
    page_obj = paginator.get_page (page_number)
    return page_obj

@login_required(login_url='login')
def home(request):
    #Seacrh facilities
    query = request.GET.get ('q','').strip()

    #show all posts latest on first
    posts = Post.objects.all().order_by('-updated_at')

    #filter if only search quesry exists
    if query:
        posts = posts.filter (
            Q(title__icontains = query) |
            Q(content__icontains = query) |
            Q(author__username__icontains = query)
        ).order_by('-updated_at')
    
    page_obj = paginate_queryset (request, posts, per_page=5)
    posts_to_render = [] # initializing at the top  
    #highlight search matches
    for post in page_obj:
        if query:
            title = mark_safe(re.sub(
                        f"({re.escape(query)})", 
                        r"<mark>\1</mark>", 
                        post.title or "", 
                        flags=re.IGNORECASE)
                    )
            content = mark_safe(re.sub(
                        f"({re.escape(query)})", 
                        r"<mark>\1</mark>", 
                        post.content or "", 
                        flags=re.IGNORECASE)
                    )
            author = mark_safe(re.sub(
                    f"({re.escape(query)})", 
                    r"<mark>\1</mark>", 
                    post.author.username or "", 
                    flags=re.IGNORECASE)
                )
       
        else: 
            title = post.title
            content = post.content
            author = post.author.username
            
        posts_to_render.append({
            'post_obj': post,
            'title': title,
            'content':content,
            'author': author,
            'created_at' : post.created_at,
            'updated_at' : post.updated_at,
            'id' : post.id,
            'author_obj':post.author,
        })
    
    return render(request, 'mainapp/home.html', {
        'posts': posts_to_render,
        'query' :query,
        'page_obj':page_obj,
        'user' :request.user,
    })

@login_required(login_url='login')
def dashboard(request):
    #Show all post created by logged in user only
    posts = Post.objects.filter (author = request.user).order_by('-updated_at') 
    page_obj = paginate_queryset (request, posts, per_page=5)
    print (page_obj)
    print (page_obj.count)
    return render(request, 'mainapp/dashboard.html', {
        'posts': page_obj,
        'page_obj':page_obj,
        })

@login_required(login_url='login')
def create_post (request):
    if request.method == "POST":
        form = PostForm (request.POST)
        if form.is_valid():                 # check blanks and othe validations
            post = form.save (commit=False) # dont save yet
            post.author = request.user      # set the logged-in user
            post.save ()
            return redirect ('home')
    else:
        form = PostForm()
  
    return render (request, 'mainapp/create_post.html', {'form': form})


@login_required(login_url='login')
def edit_post (request, id):
    post = get_object_or_404 (Post, id=id)

    if request.method == "POST":
        post.title = request.POST.get ('title')
        post.content = request.POST.get ('content')
        post.save()
        return redirect ('home')
        
    return render (request, 'mainapp/edit_post.html', {'post' : post})

@login_required(login_url='login')
def delete_post (request, id):
    post = get_object_or_404 (Post, id=id)

    if request.method == "POST":
        post.delete()
        return redirect ('home')
    
    return redirect ('home')

def signup (request):
    if request.method == "POST":
        username = request.POST.get ('username')
        password = request.POST.get ('password')

        #Check if username already exists
        if User.objects.filter (username=username).exists():
            return render (request, 'mainapp/signup.html', {
                'error' : 'Username already exists'
            })

        #Create User
        User.objects.create_user (username = username, password = password)
        
        #Rediecrt to login page after signup
        return redirect ('login')
    
    #Show signup form
    return render (request, 'mainapp/signup.html')

def login_view (request):
    if request.method =="POST":
        username = request.POST.get ('username')
        password = request.POST.get ('password')

        #autheticate User
        user = authenticate (request, username = username, password = password)

        if user is not None:
            login (request, user) #Logs the user in
            return redirect ('home')
        else:
            return render (request, 'mainapp/login.html', {'error':'Invalid Credential'})
    
    #For GET request, always return the login page        
    return render (request, 'mainapp/login.html')
    
def logout_view(request):
    logout(request) #This will end user session
    return redirect ('login') #Redirect to login page

#details of indiviaul blog
@login_required(login_url='login')
def post_details (request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render (request, 'mainapp/post_details.html',{
        'post': post,
        'user' : request.user,
    })

#like post
@login_required
def like_post(request, post_id):
    post= get_object_or_404 (Post, id = post_id)
    user = request.user
    if user in post.dislikes.all():
        post.dislikes.remove(user)
    if user in post.likes.all():
        post.likes.remove(user)
    else:
        post.likes.add(user)
    return redirect('home')

#dislike post
@login_required
def dislike_post(request, post_id):
    post= get_object_or_404 (Post, id = post_id)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
    if user in post.dislikes.all():
        post.dislikes.remove(user)
    else:
        post.dislikes.add(user)
    return redirect('home')

#post details view with comments
@login_required(login_url='login')
def post_details(request, post_id):
    #Fetch post or 404 if doesnt exist
    post = get_object_or_404(Post, id=post_id)

    #Fetch all comments for teh above post
    comments = post.comments.all().order_by('-created_at')

    #Handle comment submission
    if request.method == "POST":
        content = request.POST.get ('content')
        if content:
            Comment.objects.create (
                post=post,
                user=request.user,
                content=content
            )
    return render (request, 'mainapp/post_details.html', {
        'post':post,
        'comments':comments,
    })   