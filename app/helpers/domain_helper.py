from django.conf import settings


class DomainHelper():
    def __init__(self, request):
        self.http_host = request.META['HTTP_HOST']
        self.domain = settings.REPO_BASE_URL

    def get_domain_url(self):
        return self.domain

    def get_cookie_domain(self, complete_domain):
        end_index = self.http_host.find(":")
        temp_domain = complete_domain[:end_index]
        start_index = temp_domain.find(".")

        return temp_domain[start_index:]
