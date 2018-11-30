from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from bookx.utils import ChoiceEnum


def get_default_owner():
    return get_user_model().objects.get_or_create(
        username=settings.DEFAULT_OWNER
    )


class LoanStatus(ChoiceEnum):
    AV = "available"
    OL = "on loan"
    RQ = "requested"
    NA = "not available"


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    cover = models.ImageField(upload_to="covers/", blank=True)
    thumb = models.ImageField(upload_to="covers/", blank=True)
    published_date = models.DateTimeField(blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[(tag.name, tag.value) for tag in LoanStatus],
        default=(LoanStatus.AV.name),
    )
    owner = models.ForeignKey(
        get_user_model(), on_delete=models.SET(get_default_owner)
    )
    holder = models.ManyToManyField(
        get_user_model(), related_name="holder", through="BookHolder"
    )

    @property
    def display_author(self):
        name = self.author.split(" ")
        if len(name) > 1:
            name[-1] = name[-1] + ", "
        lastfirst = name[-1:] + name[:-1]
        return "".join(lastfirst)

    def get_absolute_url(self):
        return reverse("book_detail", kwargs={"pk": self.pk})

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    @property
    def update_url(self):
        return reverse("book_update", kwargs={"pk": self.pk})

    @property
    def delete_url(self):
        return reverse("book_delete", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title


class BookHolder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    holder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    date_requested = models.DateTimeField(blank=True, null=True)
    date_borrowed = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)
