from django.contrib.auth.models import User
from chat.models import UserProfile

print(f'Total users: {User.objects.count()}')
print(f'Total profiles: {UserProfile.objects.count()}')
print('\nUsers:')
for u in User.objects.all()[:10]:
    try:
        profile = u.profile
        print(f'  - {u.username} (id={u.id}, online={profile.is_online})')
    except:
        print(f'  - {u.username} (id={u.id}, NO PROFILE)')
