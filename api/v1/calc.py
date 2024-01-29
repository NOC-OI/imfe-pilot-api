# pylint: disable=too-many-arguments
"""
Router module for calc entrypoints.

This router contains the following functions:
    * calc_results: function for open and merge files and applied some calculation
"""

from typing import Optional

from fastapi import APIRouter

from use_cases_calc.get_bucket import GetBucket

router = APIRouter()


@router.get("/")
def calc_results(
    filenames: str,
    extension: Optional[str] = "csv",
    calc: str = "count",
    calc_columns: Optional[str] = "",
    columns: Optional[str] = None,
    drop_columns: Optional[str] = "Unnamed: 0",
    bbox: Optional[str] = "",
    crs: Optional[str] = None,
    lat_lon_columns: Optional[str] = "latitude,longitude",
    agg_columns: Optional[str] = None,
    exclude_index: Optional[bool] = False,
    all_columns: Optional[bool] = False,
):
    """
    calc_results: function for open and merge files and applied some calculation

    Args:
    filenames (Optional(str)): the names of the files, separated by comma.
                The pathname should be separated by ':'. For example, if you want to open
                the files data/file1 and data/file2, you should pass data:file1,data:file2.

    extension (Optional(str)): files extension. Defaults to 'csv'.

    calc (Optional(str)): tyoe of calculation that you want to apply to the data.
      It should be: count, unique, agg, organism, biodiversity1, biodiversity2,
        biodiversity3, biodiversity4 or biodiversity5. Default to 'count'.

    calc_columns (Optional(str)): name of the columns that you want to apply calculation.

    columns (Optional(str)): name and values of default columns to add to the the data.
      For example, if you want to add a column test with value 10 and a column data with value true,
      the value of columns should be test:10,data:true. Default is None.

    drop_columns (Optional(str)): columns that you want to drop in the final file. It should be
      separated by column name. For example: test,data. Default is 'Unnamed: 0'

    bbox (Optional(str)): limits of the data. It should have the format "xmin,ymin,xmax,ymax".
      If you are not using the same projection if the data, you should pass a value to
      argument "crs". You should also need to pass the names of lat_lon_columns.
      Default is empty.

    crs (Optional(str)): the source and the destination projection. It is necessary if you want to
      clip the data using a projection that is different of the data. Format:
      source,destination. For example: EPSG:4326,EPSG:3857'. Default is None.

    lat_lon_columns (Optional(str)): names of the latitude and longitude columns.
      For example, if your latitude and longitude data in the file has column
      names 'lat' and 'lng', you should pass a value 'lat,lng'. It is case
      sensitive. Default is latitude,longitude.

    agg_columns (Optional(str)): if you define calc type as 'agg', you should
      pass a value for agg_columns. You define the name of calculation and the
      column that you want to apply it. For example, if you want to get the
      first data of column test and get unique values of column test2, you
      should pass 'first:test,unique:test1'

    exclude_index (Optional(bool)): set to true if you want to exclude index
      in the result. Default: true

    all_columns (Optional(bool)): return all columns from the file

    Returns:
      json_data: a json structure with the calculation results
    """

    data = GetBucket()
    data.get(
        filenames=filenames,
        extension=extension,
        columns=columns,
        drop_columns=drop_columns.split(","),
        bbox=bbox,
        crs=crs,
        lat_lon_columns=lat_lon_columns.split(","),
    )

    data.do_calc(
        calc=calc,
        calc_columns=calc_columns.split(","),
        agg_columns=agg_columns,
        exclude_index=exclude_index,
        all_columns=all_columns,
    )

    return data.result
