from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
# 'Q' is used to generate a search query (mainly the 'OR' logic bit)
from django.db.models import Q
from .models import Product

# Create your views here.


def all_products(request):
    # A view to show all products, including sorting and search queries

    products = Product.objects.all()
    # Set these intially to 'None', so as not cause errors
    query = None
    sort = None
    direction = None

    if request.GET:
        if 'sort' in request.GET:
            """
            The reason for copying the sort parameter into a new variable
            called sortkey is to preserve the original field we want it to
            sort on (i.e. 'name').
            If we had just renamed 'sort' itself to 'lower_name', we would
            have lost the original field 'name'.
            """
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'name':
                sortkey = 'lower_name'
                # Annotation allows us to add a temporary field on a model
                # Our goal with 'Lower' is to make the sorting case-insensitive
                products = products.annotate(lower_name=Lower('name'))

            if 'direction' in request.GET:
                direction = request.GET['direction']
                if direction == 'desc':
                    # Adding a minus reverses the sorting order
                    sortkey = f'-{sortkey}'
            products = products.order_by(sortkey)

        """
        'q' is the value of the 'name' attribute
        assigned to the search bar in base.html
        """
        if 'q' in request.GET:
            query = request.GET['q']
            if not query:
                messages.error(request, "Please enter search criteria...")
                return redirect(reverse('products'))

            """
            The pipe ('|') is what generates the OR statement/logic
            for the queries,
            and the 'i' in front of 'contains' makes
            the queries case insensitive
            """
            queries = Q(name__icontains=query) | Q(author__icontains=query)
            products = products.filter(queries)

    current_sorting = f'{sort}_{direction}'

    context = {
        'products': products,
        'search_term': query,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    # A view to show individual product details

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)