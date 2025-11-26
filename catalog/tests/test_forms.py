from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from catalog.models import Book, Author, BookInstance
import datetime

class RenewBookLibrarianViewTest(TestCase):
    def setUp(self):
        # Создаем пользователей
        self.user1 = User.objects.create_user(username='user1', password='12345')
        self.librarian = User.objects.create_user(username='librarian', password='12345')
        permission = Permission.objects.get(codename='can_mark_returned')
        self.librarian.user_permissions.add(permission)
        self.librarian.save()

        # Создаем автора и книгу
        author = Author.objects.create(first_name='John', last_name='Doe')
        book = Book.objects.create(title='Test Book', author=author, summary='Summary', isbn='1234567890123')

        # Создаем экземпляр книги с текстовым PK
        self.book_instance = BookInstance.objects.create(
            id='ABC123',
            book=book,
            imprint='Test Imprint',
            due_back=datetime.date.today() + datetime.timedelta(days=7),
            borrower=self.user1,
            status='o'
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.book_instance.id}))
        self.assertRedirects(response, f'/accounts/login/?next=/catalog/book/{self.book_instance.id}/renew/')

    def test_form_initial_date(self):
        self.client.login(username='librarian', password='12345')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.book_instance.id}))
        proposed_date = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['renewal_date'], proposed_date)

    def test_successful_post_redirect(self):
        self.client.login(username='librarian', password='12345')
        new_date = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse('renew-book-librarian', kwargs={'pk': self.book_instance.id}),
            {'renewal_date': new_date}
        )
        self.assertRedirects(response, reverse('all-borrowed'))
        self.book_instance.refresh_from_db()
        self.assertEqual(self.book_instance.due_back, new_date)
