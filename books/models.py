from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from bookx.utils import ChoiceEnum


def get_default_owner():
    def_user = get_user_model().objects.get_or_create(
        username=settings.DEFAULT_OWNER, email=settings.DEFAULT_OWNER_EMAIL
    )
    return def_user[0]


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
    isbn = models.CharField(
        "ISBN",
        max_length=17,
        help_text='13 Character \
        <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>',
        null=True,
    )
    description = models.TextField(
        max_length=1000,
        help_text="Enter \
        a brief description of the book",
        null=True,
    )
    status = models.CharField(
        max_length=50,
        choices=[(tag.name, tag.value) for tag in LoanStatus],
        default=(LoanStatus.AV.name),
    )
    owner = models.ForeignKey(
        get_user_model(),
        related_name="books_owned",
        on_delete=models.SET(get_default_owner),
    )
    holders = models.ManyToManyField(
        get_user_model(), related_name="books_held", through="BookHolder"
    )
    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.CASCADE
    )

    def get_loan(self, status):
        latestby = self.get_latestby_for_status(status)
        try:
            loan = BookHolder.objects.filter(status=status, book=self).latest(
                latestby
            )
        except BookHolder.DoesNotExist:
            loan = None
        return loan

    def get_holder_for_status(self, status):
        loan = self.get_loan(status)
        if loan:
            return loan.holder
        else:
            return None

    def get_holder_for_current_status(self):
        return self.get_holder_for_status(self.status)

    def get_latestby_for_status(self, status):
        status_latestby = {
            "RQ": "date_requested",
            "OL": "date_borrowed",
            "AV": "date_returned",
            "NA": None,
        }
        return status_latestby[status]

    def get_date_for_status(self, status):
        loan = self.get_loan(status)
        if status == "RQ":
            date = loan.date_requested
        elif status == "OL":
            date = loan.date_borrowed
        elif status == "AV":
            date = loan.date_returned
        else:
            date = None
        return date

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

    def __str__(self):
        return self.title


class BookHolder(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    holder = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    status = models.CharField(max_length=2, default="RQ")
    date_requested = models.DateTimeField(blank=True, null=True)
    date_borrowed = models.DateTimeField(blank=True, null=True)
    date_returned = models.DateTimeField(blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
