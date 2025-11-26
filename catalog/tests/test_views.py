from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Book, Author, BookInstance
import datetime

class RenewBookLibrarianViewTest(TestCase):

    def setUp(self):
        # Создаем пользователя
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.user.save()

        # Создаем пользователя с правами библиотекаря
        self.librarian = User.objects.create_user(username='librarian', password='12345')
        permission = Permission.objects.get(codename='can_mark_returned')
        self.librarian.user_permissions.add(permission)
        self.librarian.save()

        # Создаем автора и книгу
        self.author = Author.objects.create(first_name='John', last_name='Doe')
        self.book = Book.objects.create(title='Test Book', author=self.author, summary='Test summary', isbn='1234567890123')
        
        # Создаем BookInstance с числовым id
        self.book_instance = BookInstance.objects.create(
            id=1,  # обязательно число, чтобы совпадало с <int:pk>
            book=self.book,
            imprint='Test Imprint',
            due_back=datetime.date.today() + datetime.timedelta(days=5),
            borrower=self.user,
            status='o'
        )

    def test_redirect_if_not_logged_in(self):
        """Проверяем, что неавторизованный пользователь перенаправляется на логин"""
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.book_instance.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission(self):
        """Проверяем доступ авторизованного библиотекаря"""
        self.client.login(username='librarian', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.book_instance.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Продление')
        self.assertContains(response, self.book.title)

    def test_post_successful_renewal(self):
        """Проверяем успешное продление книги через POST"""
        self.client.login(username='librarian', password='12345')
        new_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse('renew-book-librarian', kwargs={'pk': self.book_instance.pk}),
            {'renewal_date': new_date}
        )
        self.assertRedirects(response, reverse('all-borrowed'))

        # Проверяем, что дата возврата обновилась
        self.book_instance.refresh_from_db()
        self.assertEqual(self.book_instance.due_back, new_date)
