from django.db import models
from django.utils import timezone

# Customer Model
class Customer(models.Model):
    DocumentType = models.CharField(max_length=21)
    DocumentNumber = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f'{self.DocumentType} {self.DocumentNumber}'

    class Meta:
        db_table = 'customer'

# ApplicationStatus Model
class ApplicationStatus(models.Model):
    StatusDescription = models.CharField(max_length=100)
    CreationDate = models.DateTimeField(default=timezone.now)
    ModificationDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.StatusDescription
    
    class Meta:
        db_table = 'application_status'

# Application Model
class Application(models.Model):
    CustomerID = models.ForeignKey(Customer, on_delete=models.CASCADE)
    StatusID = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE)
    CreationDate = models.DateTimeField(default=timezone.now)
    ModificationDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.CustomerID} - {self.StatusID}'

    class Meta:
        db_table = 'application'

# BasicInformation Model
class BasicInformation(models.Model):
    ApplicationID = models.OneToOneField(Application, on_delete=models.CASCADE, primary_key=True)
    FirstName = models.TextField(max_length=300)  
    LastName = models.TextField(max_length=300)  
    Country = models.TextField(max_length=300)  
    State = models.TextField(max_length=300)  
    City = models.TextField(max_length=300)  
    Address = models.TextField(max_length=300)  
    MobileNumber = models.TextField(max_length=300)  
    Email = models.TextField(max_length=300)  
    CreationDate = models.DateTimeField(default=timezone.now)
    ModificationDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.FirstName} {self.LastName}'

    class Meta:
        db_table = 'basic_information'

# EconomicInformation Model
class EconomicInformation(models.Model):
    ApplicationID = models.OneToOneField(Application, on_delete=models.CASCADE, primary_key=True)
    Profession = models.CharField(max_length=100)
    EconomicActivity = models.CharField(max_length=100)
    CompanyName = models.CharField(max_length=100)
    PositionInCompany = models.CharField(max_length=100)
    CompanyContact = models.CharField(max_length=100)
    Income = models.DecimalField(max_digits=10, decimal_places=2)
    Expenses = models.DecimalField(max_digits=10, decimal_places=2)
    Assets = models.DecimalField(max_digits=10, decimal_places=2)
    Liabilities = models.DecimalField(max_digits=10, decimal_places=2)
    NetWorth = models.DecimalField(max_digits=10, decimal_places=2)
    FullAddress = models.CharField(max_length=255)
    CreationDate = models.DateTimeField(default=timezone.now)
    ModificationDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.CompanyName

    class Meta:
        db_table = 'economic_information'

# CardOffer Model
class CardOffer(models.Model):
    ApplicationID = models.ForeignKey(Application, on_delete=models.CASCADE)
    CardType = models.CharField(max_length=50)
    Franchise = models.CharField(max_length=50)
    CreditLimit = models.DecimalField(max_digits=10, decimal_places=2)
    APR = models.DecimalField(max_digits=5, decimal_places=2)
    Rewards = models.CharField(max_length=100)
    AnnualFee = models.DecimalField(max_digits=6, decimal_places=2)
    CreationDate = models.DateTimeField(default=timezone.now)
    ModificationDate = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.CardType} - {self.Franchise}'

    class Meta:
        db_table = 'card_offer'