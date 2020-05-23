s = Settings()
s.__setitem__("d", "Moin")
s.update({"s": "Hallo"})
print(str(s))
for k in s:
  print(k)
print(dict(s))
