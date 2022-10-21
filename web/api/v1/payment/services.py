from microservice_request.services import MicroServiceConnect
from django.conf import settings


class ProductsService(MicroServiceConnect):
    api_key = settings.PRODUCTS_API_KEY
    service = settings.PRODUCTS_API_URL
    PROXY_REMOTE_USER = True
    SEND_COOKIES = True

    def custom_headers(self) -> dict:
        headers = {'Host': self.request.get_host()}
        if user := self.request.remote_user:
            headers['Remote-User'] = str(user.id)
        return headers
