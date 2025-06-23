import views
from henango.urls.pattern import UrlPattern

# pathとview関数の対応
url_patterns = [
    UrlPattern("/now", views.now),
    UrlPattern("/show_request", views.show_request),
    UrlPattern("/parameters", views.parameters),
    UrlPattern("/user/<user_id>/profile", views.user_profile),
]
