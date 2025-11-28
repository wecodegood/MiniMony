def SendMessage(page, message):
    page.get_by_placeholder("Message DeepSeek").fill(message)
    page.keyboard.press("Enter")



def SendGetMessage(page, message):
    from initMods.GetLastResponse import GetLastResponse
    page.get_by_placeholder("Message DeepSeek").fill(message)
    page.keyboard.press("Enter")
    response = GetLastResponse()
    return response
    
