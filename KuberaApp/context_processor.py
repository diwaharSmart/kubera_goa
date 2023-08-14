from .models import WebsiteInfo

def website_info_context(request):
    try:
        website_info = WebsiteInfo.objects.first()  # Retrieve the first WebsiteInfo object
    except WebsiteInfo.DoesNotExist:
        website_info = None

    context = {
        'website_info': website_info
    }
    return context