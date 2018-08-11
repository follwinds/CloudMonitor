from __future__ import unicode_literals

from django.db import models

# Create your models here.
class User(models.Model):
	username=models.CharField(max_length=10)
	password=models.CharField(max_length=40)

class Threshold(models.Model):
	pcpu=models.FloatField()
	pmem=models.FloatField()
	pload=models.FloatField()
	vcpu=models.FloatField()
	vmem=models.FloatField()
	sshtv=models.FloatField()
	icmptv=models.FloatField()
	icmpntv=models.IntegerField()
	keyword=models.CharField(max_length=50)
