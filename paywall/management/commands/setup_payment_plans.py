import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from paywall.models import PaymentPlan
from decimal import Decimal

class Command(BaseCommand):
    help = 'Setup Mangi payment plans with all details'

    def handle(self, *args, **options):
        self.stdout.write('Setting up payment plans for Mangi POS...')

        # Clear existing plans to avoid duplicates
        PaymentPlan.objects.all().delete()
        self.stdout.write('Removed existing payment plans')

        # Create monthly plans
        self._create_anza_plan(plan_type='monthly')
        self._create_endeleza_plan(plan_type='monthly')
        self._create_dumu_plan(plan_type='monthly')

        # Create yearly plans with savings
        self._create_anza_plan(plan_type='yearly')
        self._create_endeleza_plan(plan_type='yearly')
        self._create_dumu_plan(plan_type='yearly')

        # Create one-time custom plan
        self._create_custom_plan()

        self.stdout.write(self.style.SUCCESS('Successfully set up all payment plans!'))

    def _create_anza_plan(self, plan_type):
        """Create the Anza (Starter) plan with appropriate pricing"""
        if plan_type == 'monthly':
            price = Decimal('4900.00')
            duration = 30
            name = "Anza (Starter)"
        else:  # yearly
            price = Decimal('49000.00')  # 10% savings
            duration = 365
            name = "Anza (Starter) - Annual"

        PaymentPlan.objects.create(
            name=name,
            description="Perfect for small businesses just getting started",
            price=price,
            duration_days=duration,
            plan_type=plan_type,
            plan_tier='anza',
            business_count=1,
            has_offline_mode=False,
            device_access="Mobile Only (Android & iOS)",
            has_advanced_inventory=False,
            has_supplier_integration=False,
            has_full_financial=False,
            has_advanced_analytics=False,
            has_multi_store=False,
            sms_tier="Limited",
            support_tier="Email Support",
            featured=False
        )
        self.stdout.write(f'Created {name} plan')

    def _create_endeleza_plan(self, plan_type):
        """Create the Endeleza (Grow) plan with appropriate pricing"""
        if plan_type == 'monthly':
            price = Decimal('12900.00')
            duration = 30
            name = "Endeleza (Grow)"
        else:  # yearly
            price = Decimal('129000.00')  # 16% savings
            duration = 365
            name = "Endeleza (Grow) - Annual"

        PaymentPlan.objects.create(
            name=name,
            description="Ideal for growing businesses",
            price=price,
            duration_days=duration,
            plan_type=plan_type,
            plan_tier='endeleza',
            business_count=3,
            has_offline_mode=True,
            device_access="Web, Windows, Mac, Mobile",
            has_advanced_inventory=False,
            has_supplier_integration=True,
            has_full_financial=True,
            has_advanced_analytics=True,
            has_multi_store=False,
            sms_tier="Standard",
            support_tier="Priority Support",
            featured=True
        )
        self.stdout.write(f'Created {name} plan')

    def _create_dumu_plan(self, plan_type):
        """Create the Dumu (Enterprise) plan with appropriate pricing"""
        if plan_type == 'monthly':
            price = Decimal('49999.00')
            duration = 30
            name = "Dumu (Enterprise)"
        else:  # yearly
            price = Decimal('499000.00')  # 17% savings
            duration = 365
            name = "Dumu (Enterprise) - Annual"

        PaymentPlan.objects.create(
            name=name,
            description="Advanced features for established businesses",
            price=price,
            duration_days=duration,
            plan_type=plan_type,
            plan_tier='dumu',
            business_count=0,  # 0 means unlimited
            has_offline_mode=True,
            device_access="Web, Windows, Mac, Mobile",
            has_advanced_inventory=True,
            has_supplier_integration=True,
            has_full_financial=True,
            has_advanced_analytics=True,
            has_multi_store=True,
            sms_tier="Advanced",
            support_tier="24/7 VIP Support",
            featured=False
        )
        self.stdout.write(f'Created {name} plan')

    def _create_custom_plan(self):
        """Create the custom one-time payment plan"""
        PaymentPlan.objects.create(
            name="Custom Solution",
            description="Tailored solutions for specific business requirements",
            price=Decimal('1200000.00'),  # Starting price
            duration_days=9999,  # Effectively lifetime
            plan_type='one_time',
            plan_tier='custom',
            business_count=0,  # Unlimited
            has_offline_mode=True,
            device_access="Custom",
            has_advanced_inventory=True,
            has_supplier_integration=True,
            has_full_financial=True,
            has_advanced_analytics=True,
            has_multi_store=True,
            sms_tier="Custom",
            support_tier="Dedicated Team",
            featured=False
        )
        self.stdout.write('Created Custom One-Time Payment plan')
