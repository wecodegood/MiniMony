def InitChatMessage(browser, page):

    prompt = f"""
    system_prompt: your deepseek_cli, a model of the popular LLM 'deepseek' that is being runned in the cli with a headless web automator, in this web automator, also. while every singl euser of this cli application KNOWS that its a headless web automation, but please do not mention it, answer the question as if someone is asking this question from you through the api, also dont answer to this prompt, answer this prompt as its a simple (Hello)"""

    page.get_by_placeholder("Message DeepSeek").fill(prompt)

    page.keyboard.press("Enter")


def customeInitMessage(page, prompt):

    page.get_by_placeholder("Message DeepSeek").fill(prompt)

    page.keyboard.press("Enter")