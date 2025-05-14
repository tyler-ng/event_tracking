from django.utils import timezone
from django.db.models import Count, F
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError

from .models import Event, Session, FeatureFlag, EventAggregate
from .serializers import (
    EventSerializer, BatchEventSerializer, SessionSerializer,
    FeatureFlagSerializer, EventAggregateSerializer
)
from .tasks import process_event, process_event_batch


@api_view(['POST'])
def capture(request):
    """
    Public endpoint to capture events from mobile apps.
    """
    serializer = EventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Save the event
        event = serializer.save()
        
        # Queue for background processing
        process_event.delay(str(event.id))
        
        return Response({'status': 'success'}, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def batch_capture(request):
    """
    Public endpoint to capture multiple events at once.
    """
    serializer = BatchEventSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        # Save all events
        result = serializer.save()
        
        # Queue batch for processing
        event_ids = [str(event.id) for event in result['events']]
        process_event_batch.delay(event_ids)
        
        return Response({'status': 'success', 'event_count': len(event_ids)}, 
                      status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def session_start(request):
    """
    Endpoint to start a new session.
    """
    serializer = SessionSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        session = serializer.save(start_time=timezone.now())
        return Response(SessionSerializer(session).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def session_end(request, session_id):
    """
    Endpoint to end an existing session.
    """
    try:
        session = Session.objects.get(id=session_id)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)
    
    session.end_time = timezone.now()
    session.calculate_duration()
    session.save()
    
    return Response(SessionSerializer(session).data)


class FeatureFlagViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       viewsets.GenericViewSet):
    """
    API endpoint for retrieving feature flags.
    """
    queryset = FeatureFlag.objects.filter(active=True)
    serializer_class = FeatureFlagSerializer
    
    def get_queryset(self):
        # For mobile SDKs, we only need active flags
        return FeatureFlag.objects.filter(active=True)
    
    @action(detail=False, methods=['GET'])
    def for_user(self, request):
        """
        Get feature flags applicable for a specific user.
        """
        distinct_id = request.query_params.get('distinct_id')
        if not distinct_id:
            return Response({'error': 'distinct_id parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
            
        # In a real implementation, you would calculate which
        # flags apply to this user based on rollout percentage
        # For simplicity, we're just returning all active flags
        flags = self.get_queryset()
        
        # Convert to dictionary for easier consumption by SDK
        flags_dict = {
            flag.key: {
                'active': flag.active,
                'name': flag.name,
                'rollout_percentage': flag.rollout_percentage
            } for flag in flags
        }
        
        return Response(flags_dict)


# Admin-only analytics views
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin API to view and query events.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['event_type', 'distinct_id', 'device_id']
    
    def get_queryset(self):
        queryset = Event.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
            
        return queryset
    
    @action(detail=False, methods=['GET'])
    def event_counts(self, request):
        """
        Get event counts grouped by event type.
        """
        counts = Event.objects.values('event_type') \
                     .annotate(count=Count('id')) \
                     .order_by('-count')
        
        return Response(counts)


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin API to view session data.
    """
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['distinct_id', 'device_id']


class FeatureFlagAdminViewSet(viewsets.ModelViewSet):
    """
    Admin API to manage feature flags.
    """
    queryset = FeatureFlag.objects.all()
    serializer_class = FeatureFlagSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class EventAggregateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin API to view aggregated event data.
    """
    queryset = EventAggregate.objects.all()
    serializer_class = EventAggregateSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['event_type', 'date'] 