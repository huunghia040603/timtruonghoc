# File này chứa các migration để tối ưu hóa database
# Chạy lệnh: python manage.py makemigrations
# Sau đó: python manage.py migrate

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('your_app_name', 'previous_migration'),  # Thay thế bằng migration trước đó
    ]

    operations = [
        # Thêm indexes cho School model
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['tag'], name='school_tag_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['school_type'], name='school_type_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['country'], name='school_country_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['start', 'end'], name='school_tuition_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['benchmark_min', 'benchmark_max'], name='school_benchmark_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['name_vn'], name='school_name_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['short_code'], name='school_code_idx'),
        ),
        migrations.AddIndex(
            model_name='school',
            index=models.Index(fields=['registration'], name='school_registration_idx'),
        ),

        # Thêm indexes cho Major model
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['major_id'], name='major_id_idx'),
        ),
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['name'], name='major_name_idx'),
        ),
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['status'], name='major_status_idx'),
        ),
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['tags'], name='major_tags_idx'),
        ),
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['school'], name='major_school_idx'),
        ),
        migrations.AddIndex(
            model_name='major',
            index=models.Index(fields=['min_tuition_fee_per_year', 'max_tuition_fee_per_year'], name='major_tuition_idx'),
        ),
    ]