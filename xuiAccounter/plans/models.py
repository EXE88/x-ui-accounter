from django.db import models

class Plan(models.Model):
    plan_name = models.CharField(max_length=150,blank=False,null=False,help_text="نام پلن")
    number_of_users = models.PositiveIntegerField(blank=False,null=False,help_text="تعداد کاربران کانفیگ")
    time = models.PositiveIntegerField(blank=False,null=False,help_text="مدت زمان کانفیگ بر حسب ماه")
    usage = models.PositiveIntegerField(blank=False,null=False,help_text="حجم کانفیگ بر حسب گیگابایت")
    price = models.PositiveIntegerField(blank=False,null=False,help_text="قیمت کانفیگ بر حسب کوین (هر کوین هزار تومن)")
