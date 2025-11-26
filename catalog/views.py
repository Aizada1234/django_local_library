from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import logout
import datetime

from .models import Book, Author, BookInstance
from .forms import RenewBookForm  # обязательно, чтобы форма работала

# -------------------- Главная страница --------------------
def index(request):
    """Главная страница сайта."""
    num_books = Book.objects.count()
    num_instances = BookInstance.objects.count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()

    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context)

# -------------------- Списки и детали --------------------
class BookListView(generic.ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'book_list'
    paginate_by = 10

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'book_detail.html'

class LoanedBooksAllListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    model = BookInstance
    template_name = 'bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')

# -------------------- Выход --------------------
from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    next_url = request.GET.get('next', 'index')
    return redirect(next_url)

# -------------------- Продление книги библиотекарем --------------------
@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    """Продление книги библиотекарем."""
    book_inst = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('all-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    return render(request, 'book_renew_librarian.html', {'form': form, 'bookinst': book_inst})
