from .models import Profile,Skill
from django.db.models import Q

from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage


# def search_profile(request):
#     search_query=''
#     if request.GET.get('search_query'):
#         search_query=request.GET.get('search_query')
#     skills=Skill.objects.filter(name__icontains=search_query)
#     profiles=Profile.objects.distinct().filter(
#         Q(name__icontains=search_query) |
#         Q(short_intro__icontains=search_query) | 
#         Q(skill__in=skills)
#         )
#     return profiles,search_query


# def paginate_profiles(request,profiles):
#     results_per_page=9
#     pages=Paginator(profiles,results_per_page)
#     page_num_range=pages.page_range
#     page_no=request.GET.get('page_no')
    
#     if not request.GET.get('page_no'):
#         page_no=1

#     left_index=int(page_no) - 4
#     if left_index < 1:
#         left_index=1

#     right_index=int(page_no) + 4
#     if right_index > len(page_num_range):
#         right_index=len(page_num_range)
    
#     custom_page_num_range=range(left_index,right_index+1)

#     last_page_num=len(page_num_range)
#     last_page_num_minus_1=last_page_num-1
    
#     try:
#         profiles=pages.page(page_no)
#     except PageNotAnInteger:
#         page_no=1
#         profiles=pages.page(page_no)
#     except EmptyPage:
#         page_no=len(page_num_range)
#         profiles=pages.page(page_no)
    

#     current_page_num=profiles.number
#     is_having_previous_page=profiles.has_previous()
#     is_having_next_page=profiles.has_next()
#     is_having_other_pages=profiles.has_other_pages()

#     if is_having_previous_page:
#         previous_page_number=profiles.previous_page_number()
#     else:
#         previous_page_number=1

#     if is_having_next_page:
#         next_page_number=profiles.next_page_number()
#     else:
#         next_page_number=current_page_num

#     context2={'page_num_range':page_num_range,'current_page_num':current_page_num,
#              'is_having_previous_page':is_having_previous_page,'is_having_next_page':is_having_next_page,
#              'previous_page_number':previous_page_number,'next_page_number':next_page_number,
#              'is_having_other_pages':is_having_other_pages,'custom_page_num_range':custom_page_num_range,
#              'last_page_num':last_page_num,'last_page_num_minus_1':last_page_num_minus_1}
    
#     return context2,profiles
