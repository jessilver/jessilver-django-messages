from django.urls import path
from .views import test_view, visual_stress_test_view, integration_test_view


urlpatterns = [
    path('', test_view, name='index'),
    path('stress/', visual_stress_test_view, name='stress-test'),
    path('integration/', integration_test_view, name='integration-test'),
]
