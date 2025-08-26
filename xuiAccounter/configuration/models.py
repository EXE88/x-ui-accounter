from django.db import models


class GlobalConfig(models.Model):
    hosts = models.TextField(
        help_text="list of subdomains/domains that will replace as host parametr in vless config (one subdomain/domain per line)"
    )
    path = models.CharField(
        max_length=255,
        help_text="subdomain/domain for path parametr in vless config"
    )
    sni = models.CharField(
        max_length=255,
        help_text="subdomain/domain for SNI paramets in vless config"
    )
    port = models.PositiveIntegerField(
        default=2053,
        help_text="service port (default : 2053)"
    )

    inbound = models.SmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Global Config"
        verbose_name_plural = "Global Configs"

    def __str__(self):
        return "Global Config"
