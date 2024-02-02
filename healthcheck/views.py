import time

from django.views.generic import TemplateView
from checker.models import Spaces, Applications, ApplicationsItem


class healthcheck(TemplateView):
    template_name = 'healthcheck.html'

    def _do_check(self):
        """Perform a basic test"""
        try:
            #breakpoint()
            ApplicationsItem.objects.exists()
            #print ("Checking")
            return True

        except Exception:
            client.captureException()
            return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["status"] = "OK" if self._do_check() else "FAIL"

        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time

        return context
