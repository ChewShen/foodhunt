from django.shortcuts import render, HttpResponse
from .models import shopLists
from django.core.paginator import Paginator


from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
import logging


# Create your views here.
def home(request):
    return render(request,"home.html")

def selectionPage(request):
    return render(request,"selectionPage.html")



# def search_shop(request):
#     if request.method == "GET":
#         searched = request.GET['searched']

#         shop_list = cyberjayaShop.objects.filter(name__icontains=searched)
#         pag = Paginator(shop_list, 10)
#         page = request.GET.get("page")
#         shops = pag.get_page(page)
#         nums = "i" * shops.paginator.num_pages
    
#         context = {
#                     'searched':searched,
#                     'shop_list': shop_list,
#                     'shops': shops,
#                     'nums': nums,
#                     }

#         return render(request, "search_shop.html",context)
    
#     else:
#         return render(request, "search_shop.html")
    


# One view handles ALL locations
def shop_list_by_location(request, area):
    # 1. Base Query: Filter by the location passed in the URL
    shops = shopLists.objects.filter(area=area).order_by("name")

    # 2. Integrate Search Logic HERE (So you stay on the same page!)
    search_query = request.GET.get('searched')
    if search_query:
        # Filter the EXISTING list, don't go to a new page
        shops = shops.filter(name__icontains=search_query)

    # 3. Pagination (Standard logic)
    paginator = Paginator(shops, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'area': area, # Pass this so the template knows where we are
        'shops': page_obj,
        'searched': search_query,
    }

    # You can reuse ONE template for all cities!
    return render(request, "shops.html", context)


from django.db.models import Q # Useful for complex queries if needed

def shop_list_view(request, area=None):
    # 1. Base Query
    if area:
        shops = shopLists.objects.filter(area=area)
    else:
        shops = shopLists.objects.all()

    # 2. SEARCH Logic
    search_query = request.GET.get('searched')
    if search_query:
        shops = shops.filter(name__icontains=search_query)

    # 3. MULTI-CUISINE FILTER (New!)
    # getlist() grabs ALL values for 'cuisine', not just the last one
    selected_cuisines = request.GET.getlist('cuisine') 
    
    if selected_cuisines:
        # Filter: Shop must match ANY of the selected cuisines
        # Logic: (cuisine contains 'chinese') OR (cuisine contains 'malay')
        query = Q()
        for c in selected_cuisines:
            query |= Q(cuisine__icontains=c)
        shops = shops.filter(query)

    # 4. SORT Logic
    sort_option = request.GET.get('sort')
    if sort_option == 'price_low':
        shops = shops.order_by('price')
    elif sort_option == 'newest':
        shops = shops.order_by('-id')
    else:
        shops = shops.order_by('name')

    # 5. PAGINATION
    paginator = Paginator(shops, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ALL_CUISINES = ['chinese', 'malay', 'indian', 'western', 'japanese', 'korean', 'cafe']

    context = {
        'area': area,
        'shops': page_obj,
        'searched': search_query,
        'current_sort': sort_option,
        'selected_cuisines': selected_cuisines, # Pass list back to template to keep checkboxes checked
        'cuisine_list': ALL_CUISINES,
    }

    return render(request, "shops.html", context)

from django.http import JsonResponse
import random

def pick_random_shop(request):
    # 1. Start with all shops
    shops = shopLists.objects.all()

    # 2. Apply Filters (Same as your main view)
    area = request.GET.get('area')
    if area:
        shops = shops.filter(area=area)

    search_query = request.GET.get('searched')
    if search_query:
        shops = shops.filter(name__icontains=search_query)
        
    # 3. Handle Cuisine Filter (New!)
    cuisine_query = request.GET.get('cuisine')
    if cuisine_query and cuisine_query != 'All':
        shops = shops.filter(cuisine__icontains=cuisine_query)

    # 4. Pick One Randomly
    candidates = list(shops.values()) # Convert to list of dicts
    
    if not candidates:
        return JsonResponse({'error': 'No shops match your filters!'}, status=404)
        
    winner = random.choice(candidates)
    
    return JsonResponse(winner)