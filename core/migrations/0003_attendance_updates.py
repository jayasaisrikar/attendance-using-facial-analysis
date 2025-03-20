from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_student_branch_alter_student_program_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='location_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendance',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='verification_method',
            field=models.CharField(choices=[('FACE', 'Face Recognition'), ('LIVENESS', 'Liveness Detection'), ('LOCATION', 'Location Verification')], default='FACE', max_length=50),
        ),
        migrations.AddField(
            model_name='attendance',
            name='confidence_score',
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name='attendance',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='attendance',
            options={'ordering': ['-date', '-created_at']},
        ),
    ] 