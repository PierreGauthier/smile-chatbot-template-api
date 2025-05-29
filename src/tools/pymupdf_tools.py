import fitz

from tools import cos_neg_sin_to_degrees
from models import PdfBbox, PdfTextBlock
EPS = 2
FONT = "NexaBold"

def is_notice_product_name(instructions_bbox:PdfBbox, text_block:PdfTextBlock):
    """Verifies whether a text-block corresponds to the product name, following the following rules:
    1- It is around 24 pixels near to the INSTRUCTIONS block
    2- Has 'NexaBold' font
    3- Has 14pt font size
    """
    distance = abs(abs(instructions_bbox.y0 - text_block.bbox.y0) - 24)
    return distance < EPS and text_block.font == FONT and text_block.size == 14.0

def extract_product_name_from_notice(pdf_path:str) -> str:
    block = extract_product_block_from_notice(pdf_path=pdf_path)
    return block.text

def extract_product_block_from_notice(pdf_path:str) -> PdfTextBlock:
    """Extract the text-block corresponding to the product name."""
    
    document = fitz.open(pdf_path)
    instructions_block = None

    for page_num in range(document.page_count):
        
        page = document.load_page(page_num)
        text_instances = page.get_text("dict")["blocks"]
        for block in text_instances:
            if block["type"] == 0: 
                for line in block["lines"]:
                    for span in line["spans"]:
                        block_rect = fitz.Rect(span["bbox"])
                        angle_point = fitz.Point(line["dir"])
                        block = PdfTextBlock(
                                page = page_num + 1,
                                text = span["text"],
                                size = span["size"],
                                font = span["font"],
                                angle = cos_neg_sin_to_degrees(angle_point.x, angle_point.y),
                                color = span["color"],
                                bbox = PdfBbox(
                                    x0 = block_rect.x0,
                                    y0 = block_rect.y0,
                                    x1 = block_rect.x1,
                                    y1 = block_rect.y1
                                )
                            )
                        
                        if not instructions_block and "INSTALLATION INSTRUCTIONS".lower() in span["text"].lower():
                            instructions_block = block
                            continue

                        if instructions_block and is_notice_product_name(instructions_bbox=instructions_block.bbox, text_block=block):
                            return block
    
    print("ERROR extracting product name")
