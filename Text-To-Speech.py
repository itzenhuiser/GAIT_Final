##
## need to:  
## brew install ffmpeg
## brew install mpv
## pip3 install elevenlabs
##

import elevenlabs
from elevenlabs import VoiceSettings  

from elevenlabs import set_api_key

set_api_key("99128584b98eb68e0e4f3289f7386063")

from elevenlabs import generate  

## possible names: Adam, Antoni, Arnold, Bill, Callum, Charlie, Clyde
  
audio = generate("ho ho ho, this shit is fucked", voice = "Bill")

from elevenlabs import play  
  
play(audio)
