from django.views.generic import ListView
from ..models import Material

class MaterialListView(ListView):
    model = Material
    template_name = "material_list.html"
    context_object_name = "materials"
