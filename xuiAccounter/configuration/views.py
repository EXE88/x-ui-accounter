from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages
import sqlite3
import os
import platform
from .models import GlobalConfig

class ConfigurePageView(UserPassesTestMixin, View):
    template_name = "configure_page.html"

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_superuser

    def handle_no_permission(self):
        return render(self.request, "403.html")

    def get(self, request):
        # DB path
        if platform.system() == "Windows":
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '../../', 'x-ui.db')
        else:
            db_path = os.path.join('/etc/x-ui/', 'x-ui.db')
        # Fetch inbounds
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, remark FROM inbounds")
        results = cursor.fetchall()
        conn.close()

        # Fetch previous config
        config = GlobalConfig.objects.filter(id=1).first()
        context = {
            'inbounds': results,
            'config': config
        }
        return render(request, self.template_name, context)

    def post(self, request):
        hosts = request.POST.get("hosts")
        port = request.POST.get("port")
        path = request.POST.get("path")
        sni = request.POST.get("sni")
        choice = request.POST.get("choice")

        try:
            config, created = GlobalConfig.objects.get_or_create(id=1, defaults={
                "hosts": hosts,
                "port": port,
                "path": path,
                "sni": sni,
                "inbound": choice,
            })
            if not created:
                config.hosts = hosts
                config.port = port
                config.path = path
                config.sni = sni
                config.inbound = choice
                config.save()
            messages.success(request, "Settings saved successfully.")
        except Exception as e:
            messages.error(request, "Error saving settings: {}".format(str(e)))

        return redirect("admin_config")