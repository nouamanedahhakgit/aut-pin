import urllib.request
data = urllib.request.urlopen('http://localhost:5001/admin/domains').read().decode('utf-8')
lines = data.split('\n')
print('Total lines:', len(lines))
for i in range(max(0, 2140), min(len(lines), 2160)):
    m = ' <<<' if i + 1 == 2145 else ''
    print(str(i+1) + ': ' + lines[i] + m)
