from django.db import models
from employees.models import Employee


class Payroll(models.Model):

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )

    month = models.CharField(max_length=20)

    year = models.IntegerField()

    basic_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    hra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    pf = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    net_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    generated_on = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.employee} - {self.month} {self.year}"