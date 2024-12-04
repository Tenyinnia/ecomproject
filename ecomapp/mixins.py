from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

# Mixin to restrict access to superusers
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        return redirect('regular_admin_page')  # Redirect regular staff to admin page

# Mixin to restrict access to staff members (includes superusers)
class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('login')  # Redirect unauthorized users to login page