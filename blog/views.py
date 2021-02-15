from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from .models import Post, Comment

from .forms import EmailPostForm, CommentForm, SearchForm
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count

from django.contrib.postgres.search import SearchVector, SearchQuery,SearchRank, TrigramSimilarity

# Create your views here.

# class PostListView(ListView):
    # """
    # this is class based view to show list of posts in blog 
    # """
    # queryset = Post.published.all()
    # context_object_name = 'posts'
    # paginate_by = 3
    # template_name = 'blog/post/list.html'
    

def post_list(request, tag_slug=None):
    """
    this is function based view to control in paginator
    """
    
    object_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in = [tag])
    
    paginator = Paginator(object_list, 3)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        #if page not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # if page is out of range deliver the last page of results
        posts = paginator.page(paginator.num_pages)
    context={'posts':posts, 
                'page':page,
                'tag':tag,
                }
    template='blog/post/list.html'
    return render(request, template, context)


# def post_list(request):
    # """
    # thi is function based view to show list of posts
    # """
    # posts = Post.published.all()
    # context={'posts':posts}
    # template='blog/post/list.html'
    # return render(request, template, context)

# def post_detail(request, year, month, day, post):
    # post = get_object_or_404(Post, slug=post, publish__year=year, publish__month=month, publish__day=day)
    # comments = post.comments.filter(active=True)
    # new_comment = None 
    # if request.method == "POST":
    #     comment_form = CommentForm(data = request.POST)
    #     if comment_form.is_valid():
    #         new_comment = comment_form.save(commit=False)
    #         new_comment.post = post
    #         new_comment.save()
    # else:
    #     comment_form = CommentForm()

    # context={
    #     'post':post,
    #     'comments': comments,
    #     'new_comment': new_comment,
    #     'comment_form': comment_form,
    #     }
    # template='blog/post/detail.html'
    # return render(request, template, context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)

    # list of similar posts
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]


    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data = request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.save()
            return redirect(post, "blog:post_detail")

    else:
        comment_form = CommentForm()

    context={
        'post': post,
        'comments': comments,
        'new_comment': new_comment,
        'comment_form': comment_form,
        'similar_posts': similar_posts, 
    }
    template = 'blog/post/detail.html'
    return render(request, template, context)

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recomends you to read {post.title}"
            message = f"Read {post.title} at {post_url} \n\n{cd['name']} Comments: {cd['comments']}"
            send_mail(subject, message, ['omarehap177@gmail.com'], [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    
    template_name = 'blog/post/share.html'
    context = {
        'post': post,
        'form': form,
        'sent': sent,
    }
    return render(request, template_name, context)


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # results = Post.published.annotate(search = SearchVector ('title', 'body')).filter(search=query)
            search_vector = SearchVector('title', weight = 'A') + SearchVector('body', weight='B')
            search_query = SearchQuery('query')
            # results = Post.published.annotate(search= search_vector, rank=SearchRank(search_vector, search_query)).filter(rank__gte=0.3).order_by['-rank']
            results = Post.published.annotate(similarity=TrigramSimilarity('title', query),).filter(similarity__gt=0.1).order_by('-similarity')

    template = 'blog/post/search.html'
    context = {
        'form': form,
        'query': query,
        'results': results,
    }
    return render(request, template, context)

















