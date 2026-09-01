try:
    from frequency_analysis import FrequencyAnalyzer
    print("Import Successful")
    
    fa = FrequencyAnalyzer()
    print("Initialization Successful")
    
    from PIL import Image
    import numpy as np
    
    # Create dummy image
    img = Image.new('RGB', (100, 100), color = 'red')
    res = fa.generate_spectrum(img)
    print(f"Generation Successful. Len: {len(res)}")
    
except Exception as e:
    print(f"Error: {e}")
