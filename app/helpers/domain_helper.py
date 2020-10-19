class DomainHelper():
    def __init__(self, request):
        self.http_host = request.META['HTTP_HOST']
        # self.domain = settings.REPO_BASE_URL
        # self.current_subdomain = 'accounts'

    def get_domain_url(self):
        return self.http_host

    # def get_service_domain_url(self, service_subdomain):
    #     return self.domain.replace(
    #         self.current_subdomain,
    #         service_subdomain
    #     )

    # def get_cookie_domain(self):
    #     start_index = self.http_host.find(".")

    #     return self.http_host[start_index:]
