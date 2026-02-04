from pathlib import Path
p=Path('input_backup.py')
s=p.read_text().splitlines()
patterns={
 'PAYMENT_TOKEN':'PAYMENT_TOKEN',
 'MAIL_SERVER_KEY':'MAIL_SERVER_KEY',
 'INTERNAL_AUTH':'INTERNAL_AUTH',
 'SQL_FMT':"'%s' % uid",
 'SHELL_TRUE':'shell=True',
 'OPEN_PATH':'with open(path)',
 'REQUESTS_POST':'requests.post(url',
 'DEBUG':'app.run(debug=True)'
}
for k,pat in patterns.items():
    for i,line in enumerate(s, start=1):
        if pat in line:
            print(k, i, line.strip())
            break
