from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'events', views.EventViewSet)
router.register(r'sessions', views.SessionViewSet)
router.register(r'feature-flags', views.FeatureFlagAdminViewSet)
router.register(r'event-aggregates', views.EventAggregateViewSet)

# Public API endpoints (no authentication required)
public_router = DefaultRouter()
public_router.register(r'feature-flags', views.FeatureFlagViewSet)

urlpatterns = [
    # Public event capture endpoints
    path('capture/', views.capture, name='capture'),
    path('batch/', views.batch_capture, name='batch_capture'),
    
    # Session management
    path('session/start/', views.session_start, name='session_start'),
    path('session/<uuid:session_id>/end/', views.session_end, name='session_end'),
    
    # Public API (for mobile SDKs)
    path('public/', include(public_router.urls)),
    
    # Admin API (requires authentication)
    path('admin/', include(router.urls)),
] 