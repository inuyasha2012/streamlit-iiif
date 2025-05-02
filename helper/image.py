import math

from PIL import Image
import io
from typing import Optional, Tuple, List, Dict
from streamlit.runtime.uploaded_file_manager import UploadedFile


def convert_image(
        uploaded_file: UploadedFile,
        scale_factors: List[int] = None,
        quality=95
) -> Tuple[Dict[str, io.BytesIO], int, int] | None:
    """
    Convert a Streamlit UploadedFile to JPEG format and create scaled versions.

    Args:
        uploaded_file: Streamlit UploadedFile object
        scale_factors: List of scaling factors (e.g., [1, 2, 4])
        quality: JPEG quality (1-100)

    Returns:
        Tuple containing:
        - Dict mapping scale factor to BytesIO image
        - Original image height
        - Original image width
    """

    try:
        # Open the uploaded file
        img = Image.open(uploaded_file)
        height = img.height
        width = img.width

        # Prepare output dictionary to store original and scaled images
        outputs = {}

        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Process each scale factor
        for scale in scale_factors:
            if scale == 1:
                # Original size image
                if img.format == 'JPEG':
                    # Use original if already JPEG
                    uploaded_file.seek(0)
                    output = io.BytesIO(uploaded_file.getvalue())
                else:
                    # Convert to JPEG
                    output = io.BytesIO()
                    img.save(output, format='JPEG', quality=quality)
                outputs['max'] = output
            else:
                scaled_width = math.ceil(width / scale)
                scaled_height = math.ceil(height / scale)
                scaled_img = img.resize((scaled_width, scaled_height))

                output = io.BytesIO()
                scaled_img.save(output, format='JPEG', quality=quality)

                output.seek(0)
                outputs[f'{scaled_width},{scaled_height}'] = output

        return outputs, height, width
    except Exception as e:
        print(f"Error converting/scaling image: {e}")
        return None