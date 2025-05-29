from models import PdfBbox

class PdfTextBlock:
    def __init__(self, page: int, text:str, size:float, font:str, bbox:PdfBbox, wmode:str=0, angle:float=0.0, color:int=0):
        self.page = page
        self.text = text
        self.wmode = wmode
        self.size = size
        self.font = font
        self.angle = angle
        self.color = color
        self.bbox = bbox