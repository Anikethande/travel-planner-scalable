from django.db import models
from django.urls import reverse
from datetime import date

# Create your models here.

class Travel(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    description = models.TextField(max_length=250)
    visits = models.IntegerField()
    image = models.CharField(default=None, blank=True, null=True, max_length=2000)

    def get_absolute_url(self):
        return reverse('detail', kwargs = {'travel_id': self.id})

    def __str__(self):
        return self.name

class Checking(models.Model):
    date = models.DateField("Checking Date")
    visit = models.CharField(default='Visited On', max_length=100)
    travel = models.ForeignKey(Travel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.get_visit_display()} on {self.date}"

    class Meta:
        ordering = ['-date']