import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='identifier',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='courserating',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='enrollment',
            options={'ordering': ('-enrolled_at',)},
        ),
        migrations.AlterModelOptions(
            name='lesson',
            options={'ordering': ('order', 'id')},
        ),
        migrations.AlterModelOptions(
            name='lessonprogress',
            options={'ordering': ('lesson',)},
        ),
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('course', 'order')},
        ),
    ]
