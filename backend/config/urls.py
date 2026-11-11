
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.decorators import login_required
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/schema/', login_required(SpectacularAPIView.as_view()), name='schema'),
    path('api/docs/', login_required(SpectacularSwaggerView.as_view(url_name='schema')), name='swagger-ui'),
]
