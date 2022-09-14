# Helper functions for converting between different metrics.

# px/96 = pt/72
class px_font_converter:
    """Converts between font size and pixel values. Returned as a floored integer
    """
    def font_size_to_pixel(self, font_size):
        """Converts font size to a pixel value as a floored int.

        Args:
            font_size (int, float): Needs to be provided as an int or float value.

        Raises:
            TypeError: If not of type int or float raises an exception.

        Returns:
            int: Returns a floored integer value.
        """
        if not isinstance(font_size, (int, float)):
            raise TypeError('font size needs to be of type int or float')
        return int(font_size*96)/72

    def pixel_to_font_size(self, px_value):
        """Converts a pixel value to a font size as a floored int.

        Args:
            px_value (int, float): Needs to be an int or float value.

        Raises:
            TypeError: If not of int or float raises an exception.

        Returns:
            int: Returns a floored integer value
        """
        if not isinstance(px_value, (int, float)):
            raise TypeError('Pixel value needs to be of type int or float')
        return int(px_value*72)/96