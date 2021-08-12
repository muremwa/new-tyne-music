from typing import List

from django.shortcuts import render
from django.views import View, generic
from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin, LoginRequiredMixin
from django.http import Http404

from .staff_actions import staff_actions


class StaffAccessMixin(UserPassesTestMixin):
    def test_func(self):
        if hasattr(self, 'request'):
            return self.request.user.is_staff or self.request.user.is_superuser

    def handle_no_permission(self):
        raise Http404


class StaffHome(StaffAccessMixin, generic.TemplateView):
    template_name = 'staff/staff_home.html'

    def user_has_perm(self, perm: str) -> bool:
        return self.request.user.has_perm(perm)

    def include_action(self, action_perms: List) -> bool:
        return all([self.user_has_perm(perm) for perm in action_perms])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'staff_actions': [action for action in staff_actions if self.include_action(action.get('permissions'))]
        })
        return context


class AddAdminUsers(LoginRequiredMixin, View):
    def get(self, *args):
        return render(self.request, 'staff/add_user.html')
