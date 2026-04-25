def get_water_mask_gee(image, region=None):
    """Единая водная маска"""
    ndwi = image.normalizedDifference(['B3', 'B8'])
    swir1 = image.select('B11')
    return (
        ndwi.gt(-0.006)
        .And(swir1.lt(1600))
    )
