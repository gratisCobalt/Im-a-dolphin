import winapps

for item in winapps.list_installed():
	print(item.name)
