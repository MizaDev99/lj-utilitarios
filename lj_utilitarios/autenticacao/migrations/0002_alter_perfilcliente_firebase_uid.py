from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('autenticacao', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilcliente',
            name='firebase_uid',
            field=models.CharField(
                blank=True,
                default=None,
                max_length=128,
                null=True,
                unique=True,
                verbose_name='Firebase UID',
            ),
        ),
    ]
