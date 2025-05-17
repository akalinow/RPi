import time

from pathlib import Path

from PIL import ImageFont

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy.font import proportional, SINCLAIR_FONT

class Display:

    ################################################
    def __init__(self, port=3, address=0x3C):

        serial = i2c(port=port, address=address)
        self.device = ssd1306(serial)
    ################################################
    def displayName(self, name):

        with canvas(self.device) as draw:
            font_path = '/scratch/akalinow/luma.examples/examples/fonts/DejaVuSansMono.ttf'
            font = ImageFont.truetype(font_path, 14)
            draw.rectangle(self.device.bounding_box, outline="white", fill="black")
            draw.text((5, 10), name, fill="white", font=font)
    ################################################

################################################        
################################################
def test_module():            
            
    if __name__ == '__main__':  
      
  
        displayObj = Display()
        displayObj.displayName("TEST")
        time.sleep(2)
        
                
#############################################
test_module()
