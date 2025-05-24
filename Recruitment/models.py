from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.validators import RegexValidator, MinLengthValidator , MaxLengthValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# use for validation = > regular expressions

# Create your models here.
class Jobseeker(models.Model) :
    user = models.OneToOneField(User , on_delete=models.CASCADE,verbose_name=_('کاربر سیستم'),help_text=_('حساب کاربری مرتبط بااین کارفرما'))
    ###
    name_validator = RegexValidator(
        regex=r'^[آ-ی\s]+\s+[آ-ی\s]+$', # \s+ => at least one space , \s[] => only one space 
        message="نام باید فقط شامل حروف فارسی و یک فاصله باشد."
    )
    full_name = models.CharField(max_length=100 , validators=[name_validator, MinLengthValidator(5)] , null =False, blank =False,
                                 verbose_name=_("نام و نام خانوادگی"))
    ###
    ###
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$', # \d{9} → only 9 charachters after 09
        message="شماره موبایل باید با '09' شروع شده و دقیقا 11 عدد باشد."
    )
    phone_number = models.CharField(max_length=11 , unique=True ,validators=[phone_validator], null = False , blank = False,
                                    verbose_name=_("شماره موبایل"))
    ###
    ###
    gpa = models.DecimalField(decimal_places=2 , max_digits=4 , default=0.00 , blank = False , null= False,validators=[MinValueValidator(0.00), MaxValueValidator(20.00)],
                              verbose_name=_("معدل"))
    ###
    skill = models.TextField(blank=True , null = True)

    class Meta:
        verbose_name = "کارجو"  # ← اینجا فارسی تعریف شده
        verbose_name_plural = "کارجوها"
    def __str__ (self) :
        return self.full_name
    def clean(self) :
        if not self.full_name.strip():
            raise ValidationError(_("نام و نام خانوادگی نمی‌تواند خالی باشد"))
        if len(self.full_name.strip().split()) < 2:
            raise ValidationError(_("لطفاً نام و نام خانوادگی را با حداقل یک فاصله وارد کنید"))
        if any(char.isdigit() for char in self.full_name):
            raise ValidationError(_("نام و نام خانوادگی نمی‌تواند شامل عدد باشد"))
        
        #gpa اعتبارسنجی فیلد 
        if self.gpa < 0.00 or self.gpa > 20.00:
            raise ValidationError(_("معدل باید بین 0.00 تا 20.00 باشد"))
        
        #  phone_number اعتبارسنجی فیلد 
        if len(self.phone_number) != 11:
            raise ValidationError(_("شماره موبایل باید دقیقاً 11 رقم باشد"))
    
        if not self.phone_number.startswith(('09', '۰۹')):
            raise ValidationError(_("شماره موبایل باید با ۰۹ شروع شود"))
    
        if not self.phone_number.isdigit():
            raise ValidationError(_("شماره موبایل باید فقط شامل اعداد باشد"))
        
class Employer(models.Model) :
    user = models.OneToOneField(User ,on_delete=models.CASCADE,
                                verbose_name=_('کاربر سیستم'),
                                help_text=_('حساب کاربری مرتبط بااین کارفرما'))
    name_validator = RegexValidator(
        regex=r'^[آ-ی\s]+\s+[آ-ی\s]+$',
        message="نام باید فقط شامل حروف فارسی و یک فاصله باشد."
    )
    full_name = models.CharField(max_length=100, validators=[name_validator], verbose_name=_("نام و نام خانوادگی"),null = True , blank = True)

    company_name = models.CharField(blank = False,
                                    null = False,unique=True,
                                    verbose_name=_('نام شرکت'),
                                    help_text=_('نام رسمی شرکت یا سازمان (حداکثر 20 کاراکتر)'),
                                    validators=[MaxLengthValidator(limit_value=20,message=_('نام شرکت نمی‌تواند بیش از 20 کاراکتر باشد'))],
                                    error_messages={'unique': _('این نام شرکت قبلاً ثبت شده است')})
    
    phone_validator = RegexValidator(
        regex=r'^09\d{9}$', # \d{9} → only 9 charachters after 09
        message="شماره موبایل باید با '09' شروع شده و دقیقا 11 عدد باشد")
    phone_number = models.CharField(max_length=11,
                                    verbose_name=_('شماره موبایل'),
                                    help_text=_('شماره تماس با فرمت ۰۹۱۲۳۴۵۶۷۸۹'),
                                    unique=True,
                                    validators=[phone_validator], null = False , blank = False)
    class Meta:
        verbose_name = "کارفرما"  # نمایش در عنوان پنل ادمین
        verbose_name_plural = "کارفرماها"  # نمایش به صورت جمع
        ordering = ['company_name']  # مرتب‌سازی بر اساس نام شرکت
        db_table = 'employers'  # نام جدول در دیتابیس
        constraints = [models.UniqueConstraint(fields=['phone_number'],name='unique_phone')]
    
    def __str__(self):
        return f"{self.company_name} - {self.phone_number}"

class project(models.Model) :
    title = models.CharField(blank=False , null = False , verbose_name=_("عنوان پروژه"),help_text=_("عنوان پروژه نمی‌تواند خالی باشد"))
    description = models.CharField(max_length=255 , null=True , blank=True,
                                   verbose_name=_("توضیحات پروژه"),
                                   help_text=_("توضیحات اختیاری درباره پروژه (حداکثر 255 کاراکتر)"))
    required_candidates = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)],
                                                      verbose_name=_("تعداد کارجو مورد نیاز"),
                                                      help_text=_("تعداد نیروی مورد نیاز برای پروژه (حداکثر 100 نفر)"))
    employer = models.ForeignKey("Employer" ,on_delete=models.CASCADE,verbose_name=_("کارفرما"),related_name='projects')

    #capacity = models.IntegerField(default=1)  # یا هر مقدار پیش‌فرض دیگر
    salary = models.DecimalField(decimal_places=2 , max_digits=10 , default=0.00,
                                 verbose_name=_("حقوق پیشنهادی (معیار دلخواه)"),
                                 help_text=_("حقوق پیشنهادی به میلیون تومان"))
    # the time that project started to begin 
    created_at = models.DateTimeField(auto_now_add=True ,verbose_name=_("تاریخ ایجاد پروژه"))

    class Meta : 
        verbose_name = _("پروژه")
        verbose_name_plural = _("پروژه‌ها")
        ordering = ['-created_at']
        constraints = [models.CheckConstraint( check = models.Q(required_candidates__lte=100), name="max_required_candidates")]

    def __str__(self):
        return f"{self.title} (کارفرما: {self.employer.company_name})"
    
    #optional 
    def clean(self):
        # اعتبارسنجی  برای عنوان
        if not self.title.strip():
            raise ValidationError({"title": _("عنوان پروژه نمی‌تواند خالی یا فقط شامل فاصله باشد")})
        # اعتبارسنجی حقوق
        if self.salary < 0:
            raise ValidationError({"salary": _("مقدار حقوق نمی‌تواند منفی باشد")})
    
    def get_absolute_url(self):
        """تولید URL برای مشاهده جزئیات پروژه"""
        return reverse('project-detail', kwargs={'pk': self.pk})

class Application(models.Model) :
    job_seeker = models.ForeignKey("Jobseeker" , on_delete=models.CASCADE,
                                   verbose_name=_('کارجو'),
                                   related_name='applications')
    project = models.ForeignKey("Project" , on_delete=models.CASCADE, verbose_name=_('پروژه'), related_name='applications' )
    class Status(models.TextChoices):
        PENDING = 'pending', _('در حال بررسی')
        APPROVED = 'approved', _('تایید شده')
        REJECTED = 'rejected', _('رد شده')
    status = models.CharField(choices=Status.choices, default=Status.PENDING, verbose_name=_('وضعیت درخواست') )
    class Meta:
        verbose_name = _('درخواست')
        verbose_name_plural = _('درخواست‌ها')
        constraints = [models.UniqueConstraint( fields=['job_seeker', 'project'], name='unique_application' )]

    def __str__(self):
        return f"{self.job_seeker} برای {self.project}"


        
        

    

