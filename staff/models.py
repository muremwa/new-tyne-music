from django.db import models
from django.utils.text import slugify


class HelpArticle(models.Model):
    title = models.CharField(max_length=1000)
    slug = models.SlugField(blank=True, null=True)
    description = models.CharField(max_length=2000)
    help_text = models.TextField()
    is_staff = models.BooleanField(default=False)
    added = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    def __str__(self):
        return f'HelpArticle: {self.title}'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)
