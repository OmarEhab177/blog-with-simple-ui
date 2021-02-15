from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager

# # Create your models here.

class PublishedManager(models.Manager):
    def get_queryset(self):
        return super(PublishedManager, self).get_queryset().filter(status='published')    
    
    
    

class Post(models.Model):
    STATUS_CHOICES=(
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique_for_date='publish')

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    
    publish = models.DateTimeField(default=timezone.now)
    crated = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    objects = models.Manager()
    published = PublishedManager()

    tags = TaggableManager()
    
    class Meta:
        ordering = ('-publish',)
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("blog:post_detail", args=(self.publish.year,self.publish.month, self.publish.day, self.slug))
    

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') 

    name = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    body = models.TextField()
    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now = True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"