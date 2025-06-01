import time, datetime

from pathlib import Path

from PIL import ImageFont
from PIL import Image

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy.font import proportional, SINCLAIR_FONT

class Display:

    ################################################
    def __init__(self, port=3, address=0x3C):

        serial = i2c(port=port, address=address)
        self.device = ssd1306(serial)

        #canvas.rectangle(self.device.bounding_box, outline="white", fill="black")

        font_path = '/scratch/akalinow/luma.examples/examples/fonts/DejaVuSansMono.ttf'
        self.font_10 = ImageFont.truetype(font_path, 10)
        self.font_14 = ImageFont.truetype(font_path, 14)
    ################################################
    def clear(self):

            self.device.clear()
            #self.device.hide()
    #################################################
    def displayMessage(self, name):

            try:
                with canvas(self.device) as draw:
                    draw.text((5, 10), name, fill="white", font=self.font_14)
                    
                    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
                    draw.text((70, 3), timestamp, fill="white", font=self.font_10)
            except:
                pass
            
    ################################################
    
################################################        
################################################
def test_module():            
            
    if __name__ == '__main__':  
      
  
        displayObj = Display()
        displayObj.displayMessage("TEST")
        time.sleep(2)
        
                
#############################################
test_module()
