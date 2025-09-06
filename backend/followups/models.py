# from django.db import models
# from django.contrib.auth.models import User
# from pydub import AudioSegment
# import os
#
# class FollowUp(models.Model):
#     class Source(models.TextChoices):
#         WHATSAPP = "WHATSAPP", "WhatsApp"
#         CALL = "CALL", "Call"
#         VERBAL = "VERBAL", "Verbal"
#         EMAIL = "EMAIL", "Email"
#         OTHER = "OTHER", "Other"
#
#     class Priority(models.TextChoices):
#         LOW = "LOW", "Low"
#         MEDIUM = "MEDIUM", "Medium"
#         HIGH = "HIGH", "High"
#
#     class Status(models.TextChoices):
#         PENDING = "PENDING", "Pending"
#         DONE = "DONE", "Done"
#         SNOOZED = "SNOOZED", "Snoozed"
#
#     owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followups")
#     source = models.CharField(max_length=16, choices=Source.choices)
#     contact_name = models.CharField(max_length=255)
#     contact_phone = models.CharField(max_length=20, null=True, blank=True)
#     description = models.TextField()
#     due_date = models.DateTimeField()
#     priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.MEDIUM)
#     status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
#     snoozed_till = models.DateTimeField(null=True, blank=True)
#     audio_note = models.FileField(upload_to="audio/", null=True, blank=True)
#     audio_mp3 = models.FileField(upload_to="audio_mp3/", null=True, blank=True)  # ✅ new field
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         ordering = ["status", "-priority", "due_date"]
#
#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         if self.audio_note and not self.audio_mp3:
#             input_path = self.audio_note.path
#             output_path = os.path.splitext(input_path)[0] + ".mp3"
#             try:
#                 audio = AudioSegment.from_file(input_path, format="webm")
#                 audio.export(output_path, format="mp3")
#                 self.audio_mp3.name = self.audio_note.name.replace(".webm", ".mp3")
#                 super().save(update_fields=["audio_mp3"])
#             except Exception as e:
#                 print("Error converting audio:", e)
#
#     def __str__(self):
#         return f"{self.contact_name} - {self.description[:30]}"
#
#


from django.db import models
from django.contrib.auth.models import User
from pydub import AudioSegment
import os

class FollowUp(models.Model):
    class Source(models.TextChoices):
        WHATSAPP = "WHATSAPP", "WhatsApp"
        CALL = "CALL", "Call"
        VERBAL = "VERBAL", "Verbal"
        EMAIL = "EMAIL", "Email"
        OTHER = "OTHER", "Other"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        DONE = "DONE", "Done"
        SNOOZED = "SNOOZED", "Snoozed"

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followups")
    source = models.CharField(max_length=16, choices=Source.choices)
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField()
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.PENDING)
    snoozed_till = models.DateTimeField(null=True, blank=True)
    audio_note = models.FileField(upload_to="audio/", null=True, blank=True)
    audio_mp3 = models.FileField(upload_to="audio_mp3/", null=True, blank=True)  # ✅ new field

    # --- Quotation Calculation Fields ---
    input1 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    input2 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    input3 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    input4 = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    formula = models.CharField(
        max_length=255,
        null=True, blank=True,
        help_text="e.g. (input1 * input2 + input3) / input4"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["status", "-priority", "due_date"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.audio_note and not self.audio_mp3:
            input_path = self.audio_note.path
            output_path = os.path.splitext(input_path)[0] + ".mp3"
            try:
                audio = AudioSegment.from_file(input_path, format="webm")
                audio.export(output_path, format="mp3")
                self.audio_mp3.name = self.audio_note.name.replace(".webm", ".mp3")
                super().save(update_fields=["audio_mp3"])
            except Exception as e:
                print("Error converting audio:", e)

    def __str__(self):
        return f"{self.contact_name} - {self.description[:30]}"

    @property
    def quotation_amount(self):
        import numexpr
        formula_str = self.formula or "(input1 * input2 + input3) / input4"
        context = {
            'input1': float(self.input1 or 0),
            'input2': float(self.input2 or 0),
            'input3': float(self.input3 or 0),
            'input4': float(self.input4 or 1),
        }
        try:
            result = numexpr.evaluate(formula_str, context)
            return round(float(result), 2)
        except Exception:
            return None
