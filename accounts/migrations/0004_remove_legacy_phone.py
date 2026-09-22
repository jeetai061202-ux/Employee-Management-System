from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_uuid_conversion"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                ALTER TABLE accounts_user
                DROP COLUMN IF EXISTS phone;
            """,
            reverse_sql="""
                ALTER TABLE accounts_user
                ADD COLUMN phone varchar(15);
            """,
        ),
    ]