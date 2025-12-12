def search(p, page):
    encoded = p.replace(' ', '%20')
    page.goto(f"https://divar.ir/s/iran?q={encoded}", wait_until="domcontentloaded") 
    pass
