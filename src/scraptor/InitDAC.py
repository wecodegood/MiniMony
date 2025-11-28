import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def InitDAC():
    # import all the functoins
    from ai.AiAnalysor.initMods.GetLastResponse import GetLastResponse
    from ai.AiAnalysor.initMods.initMessages import customeInitMessage
    from ai.AiAnalysor.initMods.Loginer import LoginToDeepSeek
    from ai.AiAnalysor.Mods.Message import SendGetMessage
    from ai.AiAnalysor.Mods.Message import SendMessage