"""
Farm Game Models for Love Chat
Fun farming game where users can plant crops, earn money, and manage their virtual farm
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import json


class Farm(models.Model):
    """User's farm with plots and farm level"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='farm')
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    energy = models.IntegerField(default=100)  # Max 100, regenerates over time
    max_energy = models.IntegerField(default=100)
    last_energy_update = models.DateTimeField(auto_now=True)
    plots_unlocked = models.IntegerField(default=6)  # Start with 6 plots
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['level']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Farm (Level {self.level})"
    
    def update_energy(self):
        """Regenerate energy over time (1 energy per 5 minutes)"""
        now = timezone.now()
        time_diff = now - self.last_energy_update
        minutes_passed = int(time_diff.total_seconds() / 60)
        
        if minutes_passed > 0:
            energy_to_add = minutes_passed // 5  # 1 energy per 5 minutes
            if energy_to_add > 0:
                self.energy = min(self.max_energy, self.energy + energy_to_add)
                self.last_energy_update = now
                self.save(update_fields=['energy', 'last_energy_update'])
        
        return self.energy
    
    def can_use_energy(self, amount=1):
        """Check if user has enough energy"""
        self.update_energy()
        return self.energy >= amount
    
    def use_energy(self, amount=1):
        """Use energy and return success"""
        if self.can_use_energy(amount):
            self.energy -= amount
            self.save(update_fields=['energy'])
            return True
        return False
    
    def add_experience(self, amount):
        """Add experience and handle level up"""
        self.experience += amount
        old_level = self.level
        
        # Level up formula: level = sqrt(experience / 100)
        new_level = int((self.experience / 100) ** 0.5) + 1
        
        if new_level > old_level:
            self.level = new_level
            # Unlock more plots every 2 levels
            if new_level % 2 == 0:
                self.plots_unlocked = min(20, self.plots_unlocked + 2)
            
            # Increase max energy every 3 levels
            if new_level % 3 == 0:
                self.max_energy = min(200, self.max_energy + 10)
                self.energy = self.max_energy  # Full energy on level up
        
        self.save()
        return new_level > old_level, new_level


class CropType(models.Model):
    """Different types of crops that can be planted"""
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    emoji = models.CharField(max_length=10, default='🌱')  # Crop emoji
    seed_price = models.IntegerField()  # Cost to buy seeds
    sell_price = models.IntegerField()  # Price when selling harvested crop
    growth_time_minutes = models.IntegerField()  # Time to grow in minutes
    experience_reward = models.IntegerField(default=1)  # XP gained when harvesting
    min_level_required = models.IntegerField(default=1)  # Minimum farm level to plant
    energy_cost = models.IntegerField(default=1)  # Energy cost to plant
    
    class Meta:
        ordering = ['min_level_required', 'growth_time_minutes']
    
    def __str__(self):
        return f"{self.emoji} {self.name}"
    
    @property
    def profit(self):
        """Profit per crop (sell price - seed price)"""
        return self.sell_price - self.seed_price
    
    @property
    def profit_per_hour(self):
        """Profit per hour for this crop"""
        if self.growth_time_minutes == 0:
            return 0
        return (self.profit * 60) / self.growth_time_minutes


class FarmPlot(models.Model):
    """Individual plot on a farm where crops can be planted"""
    PLOT_STATES = [
        ('empty', 'Empty'),
        ('planted', 'Planted'),
        ('ready', 'Ready to Harvest'),
        ('withered', 'Withered'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='plots')
    plot_number = models.IntegerField()  # Position on farm (0-19)
    state = models.CharField(max_length=20, choices=PLOT_STATES, default='empty')
    crop_type = models.ForeignKey(CropType, on_delete=models.SET_NULL, null=True, blank=True)
    planted_at = models.DateTimeField(null=True, blank=True)
    ready_at = models.DateTimeField(null=True, blank=True)
    withers_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['farm', 'plot_number']
        indexes = [
            models.Index(fields=['farm', 'plot_number']),
            models.Index(fields=['state']),
            models.Index(fields=['ready_at']),
        ]
    
    def __str__(self):
        return f"{self.farm.user.username}'s Plot {self.plot_number} ({self.state})"
    
    def plant_crop(self, crop_type):
        """Plant a crop in this plot"""
        if self.state != 'empty':
            return False, "Plot is not empty"
        
        if not self.farm.use_energy(crop_type.energy_cost):
            return False, "Not enough energy"
        
        now = timezone.now()
        self.crop_type = crop_type
        self.state = 'planted'
        self.planted_at = now
        self.ready_at = now + timedelta(minutes=crop_type.growth_time_minutes)
        self.withers_at = self.ready_at + timedelta(hours=24)  # Crops wither after 24h
        self.save()
        
        return True, "Crop planted successfully"
    
    def update_state(self):
        """Update plot state based on time"""
        if self.state == 'planted' and self.ready_at and timezone.now() >= self.ready_at:
            self.state = 'ready'
            self.save(update_fields=['state'])
        elif self.state == 'ready' and self.withers_at and timezone.now() >= self.withers_at:
            self.state = 'withered'
            self.save(update_fields=['state'])
        
        return self.state
    
    def harvest(self):
        """Harvest the crop and return rewards"""
        self.update_state()
        
        if self.state != 'ready':
            return False, "Crop is not ready to harvest", 0, 0
        
        if not self.crop_type:
            return False, "No crop planted", 0, 0
        
        # Calculate rewards
        money_earned = self.crop_type.sell_price
        experience_gained = self.crop_type.experience_reward
        
        # Add money to wallet
        wallet = self.farm.user.wallet
        wallet.add_balance(
            money_earned, 
            'farm_harvest', 
            f'Harvested {self.crop_type.name} from farm'
        )
        
        # Add experience to farm
        leveled_up, new_level = self.farm.add_experience(experience_gained)
        
        # Clear the plot
        crop_name = self.crop_type.name
        crop_emoji = self.crop_type.emoji
        self.crop_type = None
        self.state = 'empty'
        self.planted_at = None
        self.ready_at = None
        self.withers_at = None
        self.save()
        
        result_message = f"Harvested {crop_emoji} {crop_name}! Earned {money_earned:,} đồng and {experience_gained} XP"
        if leveled_up:
            result_message += f" 🎉 LEVEL UP! Now level {new_level}!"
        
        return True, result_message, money_earned, experience_gained
    
    def clear_plot(self):
        """Clear withered crops or empty the plot"""
        self.crop_type = None
        self.state = 'empty'
        self.planted_at = None
        self.ready_at = None
        self.withers_at = None
        self.save()
    
    @property
    def time_until_ready(self):
        """Get time remaining until crop is ready"""
        if self.state != 'planted' or not self.ready_at:
            return None
        
        time_left = self.ready_at - timezone.now()
        if time_left.total_seconds() <= 0:
            return None
        
        return time_left


class FarmTransaction(models.Model):
    """Track farm-related transactions (seeds, harvests, etc.)"""
    TRANSACTION_TYPES = [
        ('seed_purchase', 'Seed Purchase'),
        ('crop_harvest', 'Crop Harvest'),
        ('plot_unlock', 'Plot Unlock'),
        ('farm_upgrade', 'Farm Upgrade'),
    ]
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.IntegerField()  # Positive for earnings, negative for spending
    crop_type = models.ForeignKey(CropType, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['farm', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.farm.user.username}: {self.get_transaction_type_display()} ({self.amount:+,} đồng)"
