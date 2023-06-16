# Migrating a logfile to sqlite
```python
# load the entries module
Base.metadata.create_all(engine)
with Session() as s:
    working_date = datetime(year=2010, month=1, day=1)
    for l in diary.open('r').readlines():
        l = l[:-1]  # remove trailing newline
        try:
            working_date = datetime.strptime(l, "%Y-%m-%d")
        except:
            try:
                time, cat, subcat, desc = l.split('\t')
                time = datetime.strptime(time, '%H:%M')
                time = working_date.replace(hour=time.hour, minute=time.minute)
                e = Entry(date=time, category=cat, subcategory=subcat, description=desc)
                s.add(e)
            except:
                pass
    s.commit()
 ```