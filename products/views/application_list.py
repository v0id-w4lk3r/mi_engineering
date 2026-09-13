from django.views.generic import ListView
from ..models import Application

class ApplicationListView(ListView):
    model = Application
    template_name = "application_list.html"
    context_object_name = "applications"
