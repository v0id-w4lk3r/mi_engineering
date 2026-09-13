from django.views.generic import ListView
from ..models import Standard

class StandardListView(ListView):
    model = Standard
    template_name = "standard_list.html"
    context_object_name = "standards"
