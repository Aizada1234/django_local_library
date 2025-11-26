from django.test import TestCase
from catalog.models import Book, Author, Genre

class BookModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем автора
        author = Author.objects.create(first_name='John', last_name='Doe')
        # Создаем жанр
        genre = Genre.objects.create(name='Fantasy')
        # Создаем книгу
        cls.book = Book.objects.create(
            title='Test Book',
            author=author,
            summary='Test summary',
            isbn='1234567890123',
        )
        cls.book.genre.add(genre)

    def test_get_absolute_url(self):
        # reverse добавляет слэш, поэтому проверяем с ним
        self.assertEqual(self.book.get_absolute_url(), f'/catalog/book/{self.book.id}/')
