from django.db import models


class ActiveManager(models.Manager):
    def active(self):
        return self.filter(is_active=True, deleted=False)
    
    def inactive(self):
        return self.filter(is_active=False, deleted=True)

class Model(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created At",
        help_text="Date and time the service was created",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="Date and time the service was last updated",
    )
    deleted = models.BooleanField(default=False)

    objects = ActiveManager()

    class Meta:
        abstract = True

    def set_inactive(self):
        self.is_active = False
        self.deleted = True
        self.save()

    def set_active(self):
        self.is_active = True
        self.deleted = False
        self.save()

    def delete(self):
        self.deleted = True
        self.save()

    def restore(self):
        self.deleted = False
        self.save()

    def hard_delete(self):
        super().delete()
