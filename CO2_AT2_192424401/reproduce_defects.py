import sys, json, inspect
from pathlib import Path
sys.path.insert(0, str(Path('outputs').resolve()))
import sentinelops as s
import original_reproduction as o

alerts = [('A1',3),('A2',9),('A3',5),('A4',9),('A5',1)]
events = [(2,3),(12,30),(40,50),(5,1),(12,10),(3,4)]
queries = ['10.0.0.9','10.0.0.5','8.8.8.8']
block = ['10.0.0.5','10.0.0.9','172.16.4.2']
print('ORIGINAL ALGORITHMS (PDF comment wrapping normalised only)')
print('Alerts:', o.sort_alerts(alerts[:]))
print('Blocked:', [o.is_blocked(block,q) for q in queries])
print('Signature:', o.find_signature('FAILFAIXFAIL','FAIL'))
print('Closest:', o.closest_logins(events))
print('Empty blocklist:', repr(o.is_blocked([], 'x')))
print('\nINCREMENTAL FIXES')
source = inspect.getsource(o.sort_alerts)
for label, old, new in [('D1','j > 0','j >= 0'),
                        ('D2','alerts[j] = key','alerts[j + 1] = key')]:
    source = source.replace(old,new)
    scope = {}; exec(source,scope)
    print(label, scope['sort_alerts'](alerts[:]))
source=inspect.getsource(o.is_blocked).replace('return False','return True',1)
scope={};exec(source,scope)
print('D3', [scope['is_blocked'](block,q) for q in queries])
source=source.replace('        else:\n            return False','    return False')
scope={};exec(source,scope)
print('D4', [scope['is_blocked'](block,q) for q in queries],
      'empty:', scope['is_blocked']([], 'x'))
source=inspect.getsource(o.find_signature).replace('range(n - m)','range(n - m + 1)')
scope={};exec(source,scope)
print('D5',scope['find_signature']('FAILFAIXFAIL','FAIL'))
source=source.replace('        if j == m - 1:', '        else:')
scope={};exec(source,scope)
print('D6',scope['find_signature']('FAILFAIXFAIL','FAIL'))
source=inspect.getsource(o.closest_logins)
for label,old,new in [('D7','min_dist = 0','min_dist = math.inf'),
                       ('D8','d > min_dist','d < min_dist'),
                       ('D9','range(len(events)):\n            d',
                        'range(i + 1, len(events)):\n            d')]:
    source=source.replace(old,new)
    scope={'math':__import__('math')};exec(source,scope)
    print(label,scope['closest_logins'](events))
print('\nCORRECTED INSERTION TRACE')
a=alerts[:]
for i in range(1,len(a)):
    key=a[i];j=i-1
    while j>=0 and a[j][1]<key[1]:
        a[j+1]=a[j];j-=1
    a[j+1]=key
    print('i =',i,a)

