from rest_framework import serializers
from .models import FollowUp,User

class FollowUpSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    quotation_amount = serializers.SerializerMethodField()

    class Meta:
        model = FollowUp
        fields = "__all__"

    def get_quotation_amount(self, obj):
        # Uses the new property in your model
        return obj.quotation_amount

    def validate(self, attrs):
        status = attrs.get("status", getattr(self.instance, "status", None))
        snoozed_till = attrs.get("snoozed_till", getattr(self.instance, "snoozed_till", None))
        if status == FollowUp.Status.SNOOZED and not snoozed_till:
            raise serializers.ValidationError("Snoozing requires 'snoozed_till'.")
        return attrs







