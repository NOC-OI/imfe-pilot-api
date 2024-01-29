# pylint: disable=too-many-arguments
"""
Router module for data entrypoints.

This router contains the following functions:
    * open_csv: function for open and merge csv files on the object store
    * open_stac: function for open stac catalog and create a single json
    * open_parquet: function for open parquet data on the object store
    * open_geojson: function for open geojson data on the object store
"""

import json
from typing import Optional

from fastapi import APIRouter

from use_cases_calc.get_bucket import GetBucket

router = APIRouter()


@router.get("/csv")
def open_csv(
    filenames: str,
    columns: Optional[str] = None,
    drop_columns: Optional[str] = "Unnamed: 0",
    bbox: Optional[str] = "",
    crs: Optional[str] = None,
    lat_lon_columns: Optional[str] = "latitude,longitude",
    orient: Optional[str] = "records",
    skip_lines: Optional[int] = 0,
    convert_geom: Optional[bool] = False,
):
    """
     open_csv: function for open and merge csv files on the object store

    Args:
    filenames (Optional(str)): the names of the files, separated by comma.
        The pathname should be separated by ':'. For example, if you want to open
        the files data/file1 and data/file2, you should pass data:file1,data:file2.

    columns (Optional(str)): name and values of default columns to add to the the data.
        For example, if you want to add a column test with value 10 and a column data
        with value true, the value of columns should be test:10,data:true. Default is None.

    drop_columns (Optional(str)): columns that you want to drop in the final file. It should be
        separated by column name. For example: test,data. Default is 'Unnamed: 0'

    bbox (Optional(str)): limits of the data. It should have the format "xmin,ymin,xmax,ymax".
        If you are not using the same projection if the data, you should pass a value to
        argument "crs". You should also need to pass the names of lat_lon_columns.
        Default is empty.

    crs (Optional(str)): the source and the destination projection. It is necessary if you want to
        clip the data using a projection that is different of the data. Format: source,destination.
        For example: EPSG:4326,EPSG:3857'. Default is None.

    lat_lon_columns (Optional(str)): names of the latitude and longitude columns. For example,
        if your latitude and longitude data in the file has column names 'lat' and 'lng',
        you should pass a value 'lat,lng'. It is case sensitive. Default is latitude,longitude.

    orient (Optional(str)): Orientation of the return json file. Please see pandas documentation
        related to pd.DataFrame.to_dict to find more information. Default is records.

    skip_lines (Optional(int)): Number of the lines that you want to skip from the file. If it is
        a positive value, it will skip the first lines. If it is negative, it is skip the
        last lines.

    convert_geom (Optional(bool)): A flag that indicates if latitude and longitude will
        be converted to geometry

    Returns:
        json_data: a json structure with the data
    """

    file_names = []
    for file in filenames.split(","):
        file_names.append(f"{file}.csv")

    data = GetBucket()

    data.get_csv(
        filenames=file_names,
        columns=columns,
        drop_columns=drop_columns.split(","),
        convert_geom=convert_geom,
    )

    if bbox:
        data.clip_data(bbox, crs, lat_lon_columns.split(","))
    if skip_lines < 0:
        data.df = data.df.iloc[:skip_lines]
    if skip_lines > 0:
        data.df = data.df.iloc[skip_lines:]

    if convert_geom:
        return json.loads(data.df.to_json())
    return data.df.to_dict(orient=orient)


# @router.get("/stac")
# def open_stac(stac_path: str, stac_name: str = "catalog.json"):
#     """
#         open_stac: function for open stac catalog and create a single json

#     Args:
#         stac_path (str): path of the stac catalog on object store
#         stac_name (str, optional): name of the main catalog.
#     Defaults to 'catalog.json'.

#     Returns:
#         dict: a json file with the items and layers obtained form the stac
#     """

#     data = GetBucket()
#     layers = data.get_stac(stac_path, stac_name)

#     return layers


# @router.get("/parquet")
# def open_parquet(filenames: str):
#     """
#      open_parquet: function for open parquet data on the object store

#     Args:
#         filenames (Optional(str)): the names of the files, separated by comma.
#         The pathname should be separated by ':'

#     Returns:
#         json_data: a json structure the the download data
#     """
#     data = GetBucket()

#     data.get_parquet(filenames)

#     # if bbox:
#     #     data.clip_data()

#     return data.df.to_dict(orient="records")


# @router.get("/geojson")
# def open_geojson(filenames: str):
#     """
#      open_geojson: function for open geojson data on the object store

#     Args:
#         filenames (Optional(str)): the names of the files, separated by comma.
#         The pathname should be separated by ':'

#     Returns:
#         json_data: a json structure the the download data
#     """
#     data = GetBucket()

#     data.get_geojson(filenames)

#     # if bbox:
#     #     data.clip_data()

#     return data.df.to_dict(orient="records")
