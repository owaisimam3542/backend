from rest_framework import viewsets, permissions, decorators, response, status
from django.db.models import Q
from .models import FollowUp
from .serializers import FollowUpSerializer

class IsOwnerOrManager(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff

class FollowUpViewSet(viewsets.ModelViewSet):
    serializer_class = FollowUpSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrManager]

    def get_queryset(self):
        qs = FollowUp.objects.all()
        if not self.request.user.is_staff:
            qs = qs.filter(owner=self.request.user)
        status_ = self.request.query_params.get("status")
        if status_:
            qs = qs.filter(status=status_)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @decorators.action(detail=True, methods=["patch"])
    def mark_done(self, request, pk=None):
        fu = self.get_object()
        fu.status = fu.Status.DONE
        fu.snoozed_till = None
        fu.save(update_fields=["status","snoozed_till","updated_at"])
        return response.Response(self.get_serializer(fu).data)

    @decorators.action(detail=True, methods=["patch"])
    def snooze(self, request, pk=None):
        fu = self.get_object()
        snoozed_till = request.data.get("snoozed_till")
        if not snoozed_till:
            return response.Response({"detail":"snoozed_till required"},
                                     status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(fu, data={"status": fu.Status.SNOOZED, "snoozed_till": snoozed_till}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response({
        "username": request.user.username,
        "is_staff": request.user.is_staff,
        "id": request.user.id,
    })

