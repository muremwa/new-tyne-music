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
        pk = self.pk
        super().save()

        if not pk or not self.slug:
            self.slug = f'{slugify(self.title)}-{self.pk}'
            self.save()
