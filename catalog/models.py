from django.db import models
from django.urls import reverse  # используется для формирования URL-адресов объектов
from django.contrib.auth.models import User

class Genre(models.Model):
    """Модель, представляющая жанр книги (например: Научная фантастика, Поэзия и т.д.)"""
    name = models.CharField(max_length=200, help_text="Введите жанр книги (например: Научная фантастика)")

    def __str__(self):
        """Строковое представление модели"""
        return self.name


class Book(models.Model):
    """Модель, представляющая книгу (но не конкретный экземпляр книги)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.SET_NULL, null=True)
    summary = models.TextField(max_length=1000, help_text="Введите краткое описание книги")
    isbn = models.CharField('ISBN', max_length=13, unique=True, help_text='13-значный номер ISBN')
    genre = models.ManyToManyField(Genre, help_text="Выберите жанр книги")

    def __str__(self):
        """Строковое представление модели"""
        return self.title

    def get_absolute_url(self):
        """Возвращает URL-адрес для доступа к отдельной записи книги"""
        return reverse('book-detail', args=[str(self.id)])


class BookInstance(models.Model):
    """Модель, представляющая конкретный экземпляр книги (который может быть на руках у читателя)."""
    id = models.CharField(primary_key=True, max_length=20)
    book = models.ForeignKey('Book', on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    LOAN_STATUS = (
        ('m', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Статус экземпляра книги',
    )

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """Строковое представление экземпляра книги"""
        return f'{self.id} ({self.book.title})'


class Author(models.Model):
    """Модель, представляющая автора."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    def get_absolute_url(self):
        """Возвращает URL-адрес для доступа к определенному автору"""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """Строковое представление модели"""
        return f'{self.last_name}, {self.first_name}'
