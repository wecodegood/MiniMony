def scrool(val1, val2, page, times = 1):
	page.mouse.wheel(val1, val2)


	if times > 1:
		for i in range times:
			page.mouse.wheel(val1, val2)
	else:
		oage.mouse.wheel(val1, val2)
