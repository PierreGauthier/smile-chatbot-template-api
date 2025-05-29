import math

def cos_neg_sin_to_degrees(cosine, neg_sine):
    # Compute the angle in radians
    radians = math.atan2(-neg_sine, cosine)    
    # Convert radians to degrees
    degrees = math.degrees(radians)    
    # Normalize the result to be in the range [0, 360)
    if degrees < 0:
        degrees += 360
    return abs(degrees)