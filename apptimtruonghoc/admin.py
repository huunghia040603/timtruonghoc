from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django import forms
from ckeditor.widgets import CKEditorWidget

# Import all your models
from .models import *
# ---
## Custom Admin Site (Optional but good practice)
# ---
class TimTruongHocAdminSite(admin.AdminSite):
    site_header = 'TimTruongHoc Admin'
    site_title = 'TimTruongHoc Admin Portal'
    index_title = 'Chào mừng đến với Trang quản trị TimTruongHoc'

admin_site = TimTruongHocAdminSite(name='TimTruongHocAdmin')

# ---
## Inline Admin for Relationships
# ---

class ImageInline(admin.TabularInline):
    model = Image
    extra = 1
    fields = ['image_file', 'caption', 'uploaded_at', 'display_image_thumbnail']
    readonly_fields = ['uploaded_at', 'display_image_thumbnail']

    def display_image_thumbnail(self, obj):
        if obj.image_file:
            # Assuming image_file stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;" />',
                obj.image_file
            )
        return "No Image"
    display_image_thumbnail.short_description = 'Thumbnail'


class MajorInline(admin.TabularInline):
    model = Major
    extra = 1
    fields = ['name', 'major_id', 'status', 'tags']
    show_change_link = True



class AdmissionScoreInline(admin.TabularInline):
    model = AdmissionScore
    extra = 1
    fields = ['year', 'score']


# ---
## Custom Admin Forms for RichText Fields
# ---

class SchoolAdminForm(forms.ModelForm):
    introduction = forms.CharField(widget=CKEditorWidget(), required=False)
    scholarships = forms.CharField(widget=CKEditorWidget(), required=False)
    address = forms.CharField(widget=CKEditorWidget(), required=False) # Assuming 'address' is a RichTextField

    class Meta:
        model = School
        fields = '__all__'

class MajorAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)
    entry_requirement = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = Major
        fields = '__all__'

class AllMajorOfAllSchoolAdminForm(forms.ModelForm):
    short_description = forms.CharField(widget=CKEditorWidget(), required=False)

    job = forms.CharField(widget=CKEditorWidget(), required=False)
    suitable = forms.CharField(widget=CKEditorWidget(), required=False)
    program = forms.CharField(widget=CKEditorWidget(), required=False)
    note = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = AllMajorOfAllSchool
        fields = '__all__'

class FieldGroupAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget(), required=False)

    class Meta:
        model = FieldGroup
        fields = '__all__'


# ---
## Custom Admin for User Model
# ---
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'first_name', 'last_name', 'role', 'user_level',
        'is_staff', 'is_active_user', 'date_of_birth', 'age', 'display_user_photo','sex'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active_user', 'role', 'user_level','sex')
    search_fields = ('email', 'first_name', 'last_name', 'living_place')
    readonly_fields = ['age', 'last_login', 'date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'date_of_birth', 'living_place', 'user_photo','sex')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Role & Level', {'fields': ('role', 'user_level', 'is_active_user')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'password2', 'first_name', 'last_name',
                       'date_of_birth', 'living_place', 'role', 'user_level', 'is_active_user','sex'),
        }),
    )

    def display_user_photo(self, obj):
        if obj.user_photo:
            # Assuming user_photo stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />',
                obj.user_photo
            )
        return "No Photo"
    display_user_photo.short_description = 'Avatar'

# ---
## Admin for User-related Models
# ---

class AdminAdmin(admin.ModelAdmin):
    list_display = ['get_user_email', 'get_user_full_name', 'create']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ['create']

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_full_name.short_description = 'Full Name'

class StaffAdmin(admin.ModelAdmin):
    list_display = ['get_user_email', 'get_user_full_name', 'create', 'get_user_role']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    list_filter = ['user__role']

    def get_user_email(self, obj):
        return obj.user.email
    get_user_email.short_description = 'Email'

    def get_user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_user_full_name.short_description = 'Full Name'

    def get_user_role(self, obj):
        return obj.user.get_role_display()
    get_user_role.short_description = 'Role'

class PartnerAdmin(admin.ModelAdmin):
    list_display = ('school', 'contact_person', 'contract_start_date', 'contract_end_date', 'is_active_partner')
    list_filter = ('is_active_partner', 'contract_start_date')
    search_fields = ('school__name_vn', 'contact_person')

# ---
## Admin for School and Related Models
# ---

class FieldGroupAdmin(admin.ModelAdmin):
    form = FieldGroupAdminForm
    list_display = ('name', 'field_id', 'display_cover_thumbnail')
    search_fields = ('name', 'field_id', 'description')

    def display_cover_thumbnail(self, obj):
        if obj.cover:
            # Assuming 'logo' stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: contain; border-radius: 5px;" />',
                obj.cover
            )
        return "No cover"
    display_cover_thumbnail.short_description = 'cover'

class MajorAdmin(admin.ModelAdmin):
    form = MajorAdminForm
    list_display = ('id','name', 'major_id', 'status', 'tags', 'display_school_name', 'get_latest_admission_score')
    list_filter = ('status', 'tags', 'school')
    search_fields = ('name', 'major_id', 'description', 'school__name_vn')
    inlines = [AdmissionScoreInline] # Add inline for AdmissionScore

    def display_school_name(self, obj):
        return obj.school.name_vn if obj.school else 'N/A'
    display_school_name.short_description = 'School'
    display_school_name.admin_order_field = 'school__name_vn'

    def get_latest_admission_score(self, obj):
        latest_score = obj.admission_scores.order_by('-year').first()
        return latest_score.score if latest_score else 'N/A'
    get_latest_admission_score.short_description = 'Latest Admission Score'

class AllMajorOfAllSchoolAdmin(admin.ModelAdmin):
    form = AllMajorOfAllSchoolAdminForm
    list_display = ('name', 'all_major_id', 'field', 'tuition_fee_per_year', 'salary','training_duration')
    list_filter = ('field',)
    search_fields = ('name', 'all_major_id', 'short_description', 'job', 'program', 'field__name')

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ImageInline] # Add inline for Images

class ImageAdmin(admin.ModelAdmin):
    list_display = ('album', 'caption', 'display_image_thumbnail', 'uploaded_at')
    list_filter = ('album',)
    search_fields = ('caption', 'image_file')

    def display_image_thumbnail(self, obj):
        if obj.image_file:
            # Assuming image_file stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 5px;" />',
                obj.image_file
            )
        return "No Image"
    display_image_thumbnail.short_description = 'Image'



class AdmissionScoreAdmin(admin.ModelAdmin):
    list_display = ( 'major', 'year', 'score')
    list_filter = ('year',  'major')
    search_fields = ( 'major__name', 'year', 'score')

class SchoolAdmin(admin.ModelAdmin):
    form = SchoolAdminForm
    list_display = (
        'id','name_vn', 'name_en', 'tag', 'admission_code',
        'display_logo_thumbnail', 'established_year', 'school_type',
        'website_url', 'quota_per_year', 'start', 'end', 'registration',
        'school_level', 'is_partner_display'
    )
    list_filter = ('school_type', 'school_level', 'tag', 'country', 'registration')
    search_fields = (
        'name_vn', 'name_en', 'short_code', 'admission_code', 'address', 'email',
        'introduction', 'scholarships', 'phone_number'
    )
    readonly_fields = ['display_logo_thumbnail', 'display_cover_photo_thumbnail']
    inlines = [MajorInline] # Only MajorInline and SocialMediaLinkInline are valid here

    def display_logo_thumbnail(self, obj):
        if obj.logo:
            # Assuming 'logo' stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: contain; border-radius: 5px;" />',
                obj.logo
            )
        return "No Logo"
    display_logo_thumbnail.short_description = 'Logo'

    def display_cover_photo_thumbnail(self, obj):
        if obj.cover_photo:
            # Assuming 'cover_photo' stores URLs directly or paths that can be resolved
            return format_html(
                '<img src="{}" style="width: 100px; height: 60px; object-fit: cover; border-radius: 5px;" />',
                obj.cover_photo
            )
        return "No Cover Photo"
    display_cover_photo_thumbnail.short_description = 'Cover Photo'

    def is_partner_display(self, obj):
        return hasattr(obj, 'partner_info') and obj.partner_info.is_active_partner
    is_partner_display.boolean = True
    is_partner_display.short_description = 'Is Active Partner?'


# ---
## Register Models with Admin Site
# ---

# Register User model with CustomUserAdmin on the default admin.site
admin.site.register(User, CustomUserAdmin)
admin.site.register(Admin, AdminAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(FieldGroup, FieldGroupAdmin)
admin.site.register(Major, MajorAdmin)
admin.site.register(AllMajorOfAllSchool, AllMajorOfAllSchoolAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(AdmissionScore, AdmissionScoreAdmin)
admin.site.register(Partner, PartnerAdmin)

# If you want to use the custom TimTruongHocAdminSite, you would register like this:
# admin_site.register(User, CustomUserAdmin)
# ... and all other models with admin_site instead of admin.site
