from django.contrib.auth.models import AbstractUser
from django.db import models

# 사용자 정보
class User(AbstractUser):
    user_num = models.AutoField(primary_key=True)  # ✅ 사용자 고유 ID
    name = models.CharField(max_length=100)        # ✅ 이름
    region = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'User'  # 테이블 이름을 'user'로 지정


# 보호소 정보
class Shelter(models.Model):
    careRegNo = models.CharField(max_length=50, primary_key=True)
    careNm = models.CharField(max_length=20)
    orgNm = models.CharField(max_length=20)
    divisionNm = models.CharField(max_length=20)
    saveTrgtAnimal = models.CharField(max_length=20)
    careAddr = models.CharField(max_length=50)
    jibunAddr = models.CharField(max_length=50)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)
    weekOprStime = models.TimeField(null=True, blank=True)
    weekOprEtime = models.TimeField(null=True, blank=True)
    weekendOprStime = models.TimeField(null=True, blank=True)
    weekendOprEtime = models.TimeField(null=True, blank=True)
    careTel = models.CharField(max_length=20)

    def __str__(self):
        return self.careNm

    class Meta:
        db_table = 'Shelter'


# 유기동물 정보
class Animal(models.Model):
    desertionNo = models.CharField(max_length=20, primary_key=True)
    careRegNo = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    happenDt = models.DateField(null=True, blank=True)
    happenPlace = models.CharField(max_length=100)
    kindCd = models.CharField(max_length=10)
    upKindCd = models.CharField(max_length=10)
    upKindNm = models.CharField(max_length=20)
    kindNm = models.CharField(max_length=30)
    colorCd = models.CharField(max_length=30)
    age = models.CharField(max_length=30)
    weight = models.CharField(max_length=20)
    sexCd = models.CharField(max_length=1)
    neuterYn = models.CharField(max_length=1)
    specialMark = models.TextField(null=True, blank=True)
    processState = models.CharField(max_length=20)
    endReason = models.CharField(max_length=30, null=True, blank=True)
    updTm = models.DateTimeField(null=True, blank=True)
    rfidCd = models.CharField(max_length=30, null=True, blank=True)
    popfile1 = models.TextField(null=True, blank=True)
    vaccinationChk = models.CharField(max_length=1, null=True, blank=True)
    healthChk = models.CharField(max_length=1, null=True, blank=True)
    sfeSoci = models.CharField(max_length=1, null=True, blank=True)
    sfeHealth = models.CharField(max_length=1, null=True, blank=True)

    def __str__(self):
        return f"{self.kindNm} ({self.age})"

    class Meta:
        db_table = 'Animal'


# 유기동물 시민 신고
class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    reported_dt = models.DateField()
    reported_time = models.TimeField()
    location = models.CharField(max_length=100)
    estimated_kind = models.CharField(max_length=50)
    sex_cd = models.CharField(max_length=1)
    image_url = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20)
    description = models.TextField()

    def __str__(self):
        return f"{self.estimated_kind} - {self.location}"

    class Meta:
        db_table = 'Report'


# 입양 신청
class Adoption(models.Model):
    STATUS_CHOICES = [
        ('신청', '신청'),
        ('승인됨', '승인됨'),
        ('거절됨', '거절됨'),
        ('완료됨', '완료됨'),
    ]

    adoption_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.animal.kindNm} ({self.status})"

    class Meta:
        db_table = 'Adoption'


# 입양 후기
class Review(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE)
    rating = models.IntegerField()
    image_url = models.TextField(blank=True, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}의 후기 - {self.rating}점"

    class Meta:
        db_table = 'Review'
