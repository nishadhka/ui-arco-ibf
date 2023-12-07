# Panel App for showing xarray hvplot

1. The xarray is delivered from lazy loaded zarr stored in a cloud object (S3 bucket). 
    HVplot gridded data visulzation-https://hvplot.holoviz.org/user_guide/Gridded_Data.html
2. The lazy loading is from Kerchunk data format loaded into zarr, described in utils.py
    https://fsspec.github.io/kerchunk/
