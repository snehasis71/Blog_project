from django.db import models
from django.contrib.auth.models import User



# Create your models here.
class Post (models.Model):
    title = models.CharField (max_length = 100, blank=False, null=False)
    content = models.TextField(max_length = 2000, blank=False, null=False)
    author = models.ForeignKey (User, on_delete=models.CASCADE, default=2)
    created_at = models.DateTimeField (auto_now_add=True)
    updated_at = models.DateTimeField (auto_now=True)

    #likes dislikes
    likes = models.ManyToManyField (User, related_name='liked_posts', blank = True)
    dislikes = models.ManyToManyField (User, related_name='disliked_posts', blank = True)

    def total_likes (self):
        return self.likes.count()
    def total_dislikes (self):
        return self.dislikes.count()

    def __str__(self):
        return self.title

class Comment (models.Model):
    post = models.ForeignKey('Post', on_delete = models.CASCADE, related_name='comments')
    user = models.ForeignKey (User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"
