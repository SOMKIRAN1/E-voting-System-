from django.db import models

# ---------- Voter ----------
class Voter(models.Model):
    name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    voter_card_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# ---------- Candidate ----------
class Candidate(models.Model):
    name = models.CharField(max_length=100)
    party_name = models.CharField(max_length=100)
    constituency = models.CharField(max_length=100)
    age = models.IntegerField()
    qualifications = models.TextField()
    
    election_symbol = models.ImageField(upload_to='symbols/')
    promises = models.TextField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.party_name})"


# ---------- AdminUser ----------
class AdminUser(models.Model):
    name = models.CharField(max_length=100)
    gov_id = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
from django.db import models

class Vote(models.Model):
    voter = models.OneToOneField('Voter', on_delete=models.CASCADE)   # One voter → one vote
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE)  # Many votes per candidate
    constituency = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.voter.name} voted for {self.candidate.name}"

