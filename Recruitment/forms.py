from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.contrib.auth import get_user_model
from .models import Jobseeker, Employer , project
from django.contrib.auth.forms import PasswordChangeForm

User = get_user_model()


# forms.py


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = project
        fields = ['title', 'description', 'required_candidates', 'salary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise forms.ValidationError('عنوان پروژه باید حداقل ۵ حرف باشد.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError('توضیحات باید حداقل ۱۰ حرف داشته باشند.')
        return description

    def clean_capacity(self):
        capacity = self.cleaned_data.get('capacity')
        if capacity < 1:
            raise forms.ValidationError('ظرفیت کارجو باید حداقل ۱ باشد.')
        if capacity > 50:
            raise forms.ValidationError('ظرفیت کارجو نمی‌تواند بیشتر از ۵۰ باشد.')
        return capacity

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary < 0:
            raise forms.ValidationError('مقدار حقوق نمی‌تواند منفی باشد.')
        return salary


class BaseRegisterForm(UserCreationForm):
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        validators=[RegexValidator(r'^[آ-ی\s]+\s+[آ-ی\s]+$')],
        help_text="نام کامل با حروف فارسی و حداقل یک فاصله"
    )
    phone_number = forms.CharField(
        label="شماره موبایل",
        max_length=11,
        validators=[RegexValidator(r'^09\d{9}$')],
        help_text="مثال: ۰۹۱۲۳۴۵۶۷۸۹"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2', 'full_name', 'phone_number']

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Username already exists")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and Jobseeker.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data.get('full_name')
        user.phone_number = self.cleaned_data.get('phone_number')
        if commit:
            user.save()
        return user

class JobSeekerRegisterForm(BaseRegisterForm):
    gpa = forms.DecimalField(
        label="معدل",
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(20.00)],
        required=False
    )

class EmployerRegisterForm(BaseRegisterForm):
    company_name = forms.CharField(
        label="نام شرکت",
        max_length=20,
        help_text="حداکثر ۲۰ کاراکتر"
    )

    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if company_name and Employer.objects.filter(company_name__iexact=company_name).exists():
            raise ValidationError("The company is already registered")
        return company_name


class JobseekerProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=100,
        help_text="فقط حروف فارسی و یک فاصله بین نام و نام خانوادگی",
        widget=forms.TextInput(attrs={'placeholder': 'مثال: علی رضایی'})
    )
    gpa = forms.DecimalField(
        label="معدل",
        max_digits=4,
        decimal_places=2,
        min_value=0.0,
        max_value=20.0,
        required=False,
        widget=forms.NumberInput(attrs={'placeholder': 'مثال: 17.50'})
    )
    skill = forms.CharField(
        label="مهارت‌ها",
        required=False,
        widget=forms.Textarea(attrs={'placeholder': 'مثال: Python, Photoshop, Excel', 'rows': 3})
    )

    class Meta:
        model = Jobseeker
        fields = ['full_name', 'gpa', 'skill']

class EmployerProfileForm(forms.ModelForm):
    company_name = forms.CharField(
        label="نام شرکت",
        max_length=20,
        help_text="حداکثر ۲۰ کاراکتر",
        widget=forms.TextInput(attrs={'placeholder': 'مثال: شرکت فناوری آریا'})
    )

    class Meta:
        model = Employer
        fields = ['company_name']

from django.contrib.auth.forms import PasswordChangeForm

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="رمز عبور فعلی",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    new_password1 = forms.CharField(
        label="رمز عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="رمز عبور جدید باید حداقل ۸ کاراکتر باشد.",
        required=False
    )
    new_password2 = forms.CharField(
        label="تکرار رمز عبور جدید",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        old = cleaned_data.get("old_password")
        new1 = cleaned_data.get("new_password1")
        new2 = cleaned_data.get("new_password2")

        if old or new1 or new2:
            # اگه یکی پر بود، بقیه هم باید پر باشن
            if not old:
                raise ValidationError("برای تغییر رمز عبور، رمز فعلی را وارد کنید.")
            if not new1:
                raise ValidationError("برای تغییر رمز عبور، رمز جدید را وارد کنید.")
            if not new2:
                raise ValidationError("برای تغییر رمز عبور، تکرار رمز جدید را وارد کنید.")
            if new1 != new2:
                raise ValidationError("رمزهای جدید واردشده با هم مطابقت ندارند.")

        return cleaned_data

    def clean_old_password(self):
        """
        بررسی صحت رمز عبور فعلی فقط اگر کاربر خواست پسورد رو عوض کنه.
        """
        old_password = self.cleaned_data.get("old_password")
        if old_password:
            if not self.user.check_password(old_password):
                raise ValidationError("رمز عبور فعلی نادرست است.")
        return old_password

class EditProjectForm(forms.ModelForm):
    class Meta:
        model = project
        fields = ['title', 'description', 'required_candidates', 'salary']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 5:
            raise ValidationError('عنوان پروژه باید حداقل ۵ کاراکتر باشد.')
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise ValidationError('توضیحات باید حداقل ۱۰ کاراکتر باشد.')
        return description

    def clean_required_candidates(self):
        required = self.cleaned_data.get('required_candidates')
        if required < 1:
            raise ValidationError('ظرفیت باید حداقل ۱ نفر باشد.')
        if required > 50:
            raise ValidationError('حداکثر ظرفیت مجاز ۵۰ نفر است.')
        return required

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary < 0:
            raise ValidationError('حقوق نمی‌تواند منفی باشد.')
        return salary