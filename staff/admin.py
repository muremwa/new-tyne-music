from django.contrib import admin

from .models import HelpArticle


@admin.register(HelpArticle)
class HelpArticleModelAdmin(admin.ModelAdmin):
    list_display = ['title', 'modified', 'is_staff']
    exclude = ('slug',)
    actions = ['make_staff', 'make_normal']

    def make_staff(self, request, query_set):
        qs = query_set.update(is_staff=True)
        self.message_user(request, f'{qs} {"articles" if qs > 1 else "article"} made staff articles')

    def make_normal(self, request, query_set):
        qs = query_set.update(is_staff=False)
        self.message_user(request, f'{qs} {"articles" if qs > 1 else "article"} made normal articles')
