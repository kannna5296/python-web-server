import views
from henango.urls.pattern import UrlPattern

# pathとview関数の対応
url_patterns = [
    UrlPattern("/now", views.now),
    UrlPattern("/show_request", views.show_request),
    UrlPattern("/parameters", views.parameters),
    UrlPattern("/user/<user_id>/profile", views.user_profile),
    UrlPattern("/set_cookie", views.set_cookie),
    UrlPattern("/login", views.login),
    # ステータスコード302は一時的なリダイレクトを意味し、ブラウザはLocationヘッダーで指定されたURLへ再度リクエストをし直してくれます。
    UrlPattern("/welcome", views.welcome),
]
