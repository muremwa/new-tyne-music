from django.forms.widgets import Textarea


class MarkdownEditor(Textarea):
    template_name = 'staff/editor/widgets/editor.html'

    class Media:
        css = {
            'all': ('css/editor/editor.css', 'css/editor/preview.css')
        }
        js = (
            'js/editor/dep/marked.min.js', 'js/editor/edt/editor.js', 'js/editor/edt/preview.js',
            'js/editor/edt/tabMaster.js',
        )
