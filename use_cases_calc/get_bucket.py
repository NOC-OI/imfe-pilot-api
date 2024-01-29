# pylint: disable=too-many-arguments
# pylint: disable=invalid-name
# pylint: disable=unpacking-non-sequence
# pylint: disable=dangerous-default-value
# pylint: disable=consider-using-dict-items
# pylint: disable=consider-iterating-dictionary
# pylint: disable=import-error
# pylint: disable=too-many-instance-attributes
# pylint: disable=unused-variable
# pylint: disable=unused-argument

"""
  GetBucket Class: class for get data and manage some calculations
  on csv, geojson and parquet data
"""
import math
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from use_cases_calc.organisms import all_organisms, all_organisms2

load_dotenv()


class GetBucket:
    """
    GetBucket class for get data and manage some calculations on csv, geojson and parquet data

    This class has the following methods:
        * get: get data from the files
        * do_calc: apply some calculations on the data
        * biodiversity5: calculation of simpson index
        * biodiversity4: calculation of shannon index
        * biodiversity3: calculation of number of morphotypes
        * biodiversity2: calculation of diversity across survey
        * biodiversity1: calculation of diversity by substrate
        * organism_calculation: apply some calculation on the organisms columns
        * agg_calculation: apply some calculation based on agg values
        * clip_data: clip data based on a bbox
        * get_geojson: function for open geojson data on the object store
        * get_parquet: function for open parquet data on the object store
        * get_csv: function for open and merge csv files on the object store
        * get_stac: function for open stac catalog and create a single json
    """

    def __init__(
        self,
        bucket: str = "haig-fras",
        base_url: str = None,
    ):
        """
        GetBucket class constructor. If you are planning to use parquet data, it
        is important to set some ENV variables related to object store.
        - JASMIN_API_URL
        - JASMIN_TOKEN
        - JASMIN_SECRET

        Args:
        bucket (str, optional): bucket name. Defaults to 'haig-fras'.
        base_url (_type_, optional): default bucket url. Defaults to
            None.
        """

        self.bucket = bucket

        # self.__jasmin_api_url = os.environ.get("JASMIN_API_URL")
        # self.__jasmin_token = os.environ.get("JASMIN_TOKEN")
        # self.__jasmin_secret = os.environ.get("JASMIN_SECRET")
        if not base_url:
            base_url = os.environ.get("JASMIN_API_URL")
        self.base_url = f"{base_url}{self.bucket}/"

        self.result = {}
        self.df = None
        self.client = None

    def get(
        self,
        filenames: str,
        extension: str,
        columns: str,
        drop_columns,
        bbox: str,
        crs: str,
        lat_lon_columns: str,
    ):
        """
        get: get data from the files

        Args:
            filename (str): name of the file in jasmin object store
            extension (str): the extension of the file
            column (str): columns that you want to do add in your return
            drop_column (str): columns that you want to remove from your return
            bbox (str): limits of the data. It should have the format "xmin, ymin, xmax, ymax"
            crs (str): the projection of the bbox. Should be 'epsg:4326' or 'epsg:3857'
            lat_lon_columns (str): columns that represents your latitude and longitude data

        Returns:
            A json file with the data or the results of calculations
        """
        # if extension == "parquet":
        #     self.get_parquet(filenames)
        # elif extension == "geojson":
        #     self.get_geojson(filenames)
        # elif extension == "csv":
        if extension == "csv":
            file_names = []
            for file in filenames.split(","):
                file_names.append(f"{file}.{extension}")
            self.get_csv(
                filenames=file_names, columns=columns, drop_columns=drop_columns
            )
        if bbox:
            self.clip_data(bbox, crs, lat_lon_columns)

        return self.df

    def do_calc(
        self,
        calc: str,
        calc_columns: str,
        agg_columns: str,
        exclude_index: bool,
        all_columns: bool,
    ):
        """
        do_calc: apply some calculations on the data

        Args:
        calc (str): type of calculation that you want to apply to the data.
            It should be: count, unique, agg, organism, biodiversity1, biodiversity2,
            biodiversity3, biodiversity4 or biodiversity5. Default to 'count'.

        calc_columns (str): name of the columns that you want to apply calculation.

        agg_columns (str): if you define calc type as 'agg', you should
            pass a value for agg_columns. You define the name of calculation and
            the column that you want to apply it. For example, if you want to get
            the first data of column test and get unique values of column test2,
            you should pass 'first:test,unique:test1'

        exclude_index (bool): set to true if you want to exclude index
            in the result.

        all_columns (Optional(bool)): return all columns from the file

        Returns:
            json_data: a json structure with the calculation results
        """
        print(exclude_index)

        calc = calc.split(",")

        for calc_column in calc_columns:
            self.result[calc_column] = {}
            for calc_type in calc:
                if calc_type == "count":
                    self.result[calc_column]["Number"] = [
                        len(self.df[calc_column].unique())
                    ]
                if calc_type == "unique":
                    if not all_columns:
                        self.result[calc_column]["Types"] = (
                            self.df.groupby(calc_column)
                            .first()
                            .reset_index()[[calc_column, "filename"]]
                            .values.tolist()
                        )
                    else:
                        df = self.df.groupby(calc_column).first().reset_index()
                        for column in self.df.columns:
                            if column == "Start date":
                                new_df = pd.to_datetime(df[column], format="%d/%m/%Y")
                                self.result[column] = [new_df.min(), new_df.max()]
                            else:
                                new_df = (
                                    df.groupby(column).first().reset_index()[[column]]
                                )
                                self.result[column] = []
                                for idx, row in new_df.iterrows():
                                    # print(idx)
                                    self.result[column].append(
                                        {"value": row[column], "label": row[column]}
                                    )
                    if not all_columns:
                        self.result = self.result[[calc_column, "filename"]]
                    print(self.result)
                    self.result.values()
                if calc_type == "agg":
                    self.agg_calculation(agg_columns, calc_column)
                if calc_type == "organism":
                    self.organism_calculation(agg_columns, calc_column)

                if calc_type == "biodiversity1":
                    self.biodiversity1(calc_column)

                if calc_type == "biodiversity2":
                    self.biodiversity2(calc_column)

                if calc_type == "biodiversity3":
                    self.biodiversity3(calc_column)

                if calc_type == "biodiversity4":
                    self.biodiversity4(calc_column)

                if calc_type == "biodiversity5":
                    self.biodiversity5(calc_column)

    def biodiversity5(self, calc_column: str):
        """
        biodiversity5: calculation of simpson index

        Args:
            calc_column (str): name of the column that you want to apply the
        calculation
        """

        self.result[calc_column]["Types"] = []
        list_unique = self.df[calc_column].unique()
        for unique_c in list_unique:
            new_result = {}
            column_result = []
            new_df = self.df[self.df[calc_column] == unique_c]
            try:
                new_df = new_df[all_organisms]
            except KeyError:
                new_df = new_df[all_organisms2]
            for idx, row in new_df.iterrows():
                total = 0
                sum_values = np.sum(row.values)
                if sum_values:
                    for val in row.values:
                        total += (val / sum_values) * (val / sum_values)
                    column_result.append(1 / total)
                print(idx)
            new_result[calc_column] = unique_c
            new_result["Result"] = (
                str(np.mean(column_result).round(2))
                + " +/- st dev "
                + str(np.std(column_result).round(2))
            )
            self.result[calc_column]["Types"].append(new_result)

    def biodiversity4(self, calc_column: str):
        """
        biodiversity4: calculation of shannon index

        Args:
            calc_column (str): name of the column that you want to apply the
        calculation
        """

        self.result[calc_column]["Types"] = []
        list_unique = self.df[calc_column].unique()
        for unique_c in list_unique:
            new_result = {}
            column_result = []
            new_df = self.df[self.df[calc_column] == unique_c]
            try:
                new_df = new_df[all_organisms]
            except KeyError:
                new_df = new_df[all_organisms2]
            for idx, row in new_df.iterrows():
                print(idx)
                total = 0
                sum_values = np.sum(row.values)
                for val in row.values:
                    if val != 0:
                        total += (val / sum_values) * math.log(val / sum_values)
                column_result.append(math.exp(-total))

            new_result[calc_column] = unique_c
            new_result["Result"] = (
                str(np.mean(column_result).round(2))
                + " +/- st dev "
                + str(np.std(column_result).round(2))
            )
            self.result[calc_column]["Types"].append(new_result)

    def biodiversity3(self, calc_column: str):
        """
        biodiversity3: calculation of number of morphotypes

        Args:
            calc_column (str): name of the column that you want to apply the
        calculation
        """
        self.result[calc_column]["Types"] = []
        list_unique = self.df[calc_column].unique()
        for unique_c in list_unique:
            new_result = {}
            column_result = []
            new_df = self.df[self.df[calc_column] == unique_c]
            try:
                new_df = new_df[all_organisms]
            except KeyError:
                new_df = new_df[all_organisms2]
            for idx, row in new_df.iterrows():
                print(idx)
                column_result.append(len(row[row > 0]))
            new_result[calc_column] = unique_c
            new_result["Number"] = (
                str(np.mean(column_result).round(1))
                + " +/- st dev "
                + str(np.std(column_result).round(1))
            )
            self.result[calc_column]["Types"].append(new_result)

    def biodiversity2(self, calc_column: str):
        """
        biodiversity2: calculation of diversity across survey

        Args:
            calc_column (str): name of the column that you want to apply the
        calculation
        """

        self.df = self.df.sum()
        try:
            self.df = self.df[all_organisms]
        except KeyError:
            self.df = self.df[all_organisms2]
        self.df = self.df[self.df > 0]
        self.result[calc_column]["Number of morphotypes"] = [len(self.df)]

    def biodiversity1(self, calc_column: str):
        """
        biodiversity1: calculation of diversity by substrate

        Args:
            calc_column (str): name of the column that you want to apply the
        calculation
        """
        try:
            self.df["sum_organisms"] = (self.df[all_organisms]).sum(axis=1)
        except KeyError:
            self.df["sum_organisms"] = (self.df[all_organisms2]).sum(axis=1)

        self.df["relation_seabed_organism"] = (
            self.df["sum_organisms"] / self.df["Area_m2"]
        )
        self.df = self.df[["relation_seabed_organism", calc_column]]
        self.df = self.df.groupby(calc_column).agg([np.mean, np.std])
        self.df = self.df.round(3)
        self.df.columns = ["mean", "std"]
        self.df["Density (individuals m-2)"] = (
            self.df["mean"].astype(str) + " +/- st dev " + self.df["std"].astype(str)
        )
        self.df.drop(columns=["mean", "std"], inplace=True)
        self.result = {}
        self.result[calc_column] = {}
        self.result[calc_column]["Types"] = self.df.reset_index().to_dict(
            orient="records"
        )

    def organism_calculation(self, agg_columns: str, calc_column: str):
        """
        organism_calculation: apply some calculation on the organisms columns

        Args:
        agg_columns (str): You define the name of calculation and
            the column that you want to apply it. For example, if you want to get
            the first data of column test and get unique values of column test2,
            you should pass 'first:test,unique:test1'

        calc_column (str): name of the column that you want to apply the
            calculation
        """

        self.df[calc_column] = pd.to_numeric(
            self.df[calc_column], downcast="integer", errors="coerce"
        )
        new_df = self.df[self.df[calc_column] > 0]
        agg_columns = agg_columns.split(",")
        agg_calcs = {}
        get_first = []
        get_density = None
        for agg in agg_columns:
            agg = agg.split(":")
            if agg[0] == "first":
                get_first.append(agg)
            elif agg[0] == "density":
                get_density = agg[1]
            else:
                agg_calcs[agg[1]] = agg[0]
        self.result[calc_column]["Information"] = []
        result_values = {}
        if len(get_first) > 0:
            for first in get_first:
                result_values[first[1]] = new_df.iloc[0][first[1]]
        if get_density:
            sum_organism = self.df[calc_column].sum()
            area = pd.to_numeric(
                self.df[get_density], downcast="integer", errors="coerce"
            ).sum()
            result_values["Density (individuals ha-1)"] = sum_organism / area * 10000
        if agg_calcs:
            dict_temp = new_df.agg(agg_calcs).to_dict()
            for key, value in dict_temp.items():
                if key == calc_column:
                    if get_density:
                        key = "Number of Specimens"
                        value = str(round(value))

                    else:
                        key = "Number"
                result_values[key] = value
        self.result[calc_column]["Information"].append(result_values)

    def agg_calculation(self, agg_columns, calc_column):
        """
        agg_calculation: apply some calculation based on agg values

        Args:
        agg_columns (str): You define the name of calculation and
            the column that you want to apply it. For example, if you want to get
            the first data of column test and get unique values of column test2,
            you should pass 'first:test,unique:test1'

        calc_column (str): name of the column that you want to apply the
            calculation
        """

        agg_columns = agg_columns.split(",")
        agg_calcs = {}
        new_columns = []
        get_first = None
        for agg in agg_columns:
            agg = agg.split(":")
            if agg[0] == "first":
                get_first = agg[1]
            if agg[0] in "density":
                agg[0] = "sum"
                for i in all_organisms:
                    agg_calcs[i] = agg[0]
                    new_columns.append(i)
            else:
                agg_calcs[agg[1]] = agg[0]
                if agg[0] in "count":
                    new_columns.append("Number")
                else:
                    new_columns.append(agg[1])

        if get_first:
            result = (
                self.df.sort_values(get_first, ascending=False)
                .groupby(calc_column)
                .agg(agg_calcs)
            )
        else:
            result = self.df.groupby(calc_column).agg(agg_calcs)
        result.columns = new_columns
        result = result.round()
        self.result[calc_column]["Types"] = result.reset_index().to_dict(
            orient="records"
        )

    def clip_data(self, bbox: str, crs: str, lat_lon_columns: str):
        """
        clip_data: clip data based on a bbox

        Args:
        bbox (str): limits of the data. It should have the format "xmin,ymin,xmax,ymax".
            If you are not using the same projection if the data, you should pass a value to
            argument "crs". You should also need to pass the names of lat_lon_columns.

        crs (str): the source and the destination projection. It is necessary if you want to
            clip the data using a projection that is different of the data.
            Format: source,destination. For example: EPSG:4326,EPSG:3857'.

        lat_lon_columns (str): names of the latitude and longitude columns. For example,
            if your latitude and longitude data in the file has column names 'lat' and 'lng',
            you should pass a value 'lat,lng'. It is case sensitive.
        """
        if "geometry" not in self.df.columns:
            self.df = gpd.GeoDataFrame(
                self.df,
                geometry=gpd.points_from_xy(
                    self.df[lat_lon_columns[1]],
                    self.df[lat_lon_columns[0]],
                    crs="EPSG:4326",
                ),
            )

        xmin, ymin, xmax, ymax = bbox.split(",")

        crs = crs.split(",")
        # if len(crs) > 1:
        #     transformer = pyproj.Transformer.from_crs(crs[0], crs[1])
        #     xmin, ymin = transformer.transform(xmin, ymin)
        #     xmax, ymax = transformer.transform(xmax, ymax)

        final_bbox = [float(xmin), float(ymin), float(xmax), float(ymax)]

        self.df = gpd.clip(gdf=self.df, mask=final_bbox, keep_geom_type=False)
        self.df.drop(columns="geometry", inplace=True)

    # def get_geojson(self, filename: str):
    #     """
    #     get_geojson: function for open geojson data on the object store

    #     Args:
    #     filenames (Optional(str)): the names of the files, separated by comma.
    #         The pathname should be separated by ':'

    #     """

    #     response = requests.get(
    #         f"{self.base_url}geojson/{filename}.geojson", timeout=10
    #     )

    #     data = response.json()
    #     self.df = gpd.GeoDataFrame.from_features(data["features"])

    # def get_parquet(self, filenames: str):
    #     """
    #     get_parquet: function for open parquet data on the object store

    #     Args:
    #     filenames (str): the names of the files, separated by comma.
    #         The pathname should be separated by ':'
    #     """

    #     self.client = self.create_client()

    #     remote_path = f"s3://{self.bucket}/geojson/{filenames}.parquet"
    #     with self.client.open(
    #         remote_path, mode="rb", s3={"profile": "default"}
    #     ) as remote_file:
    #         self.df = gpq.read_geoparquet(remote_file)

    def get_csv(
        self,
        filenames: str,
        columns: str = None,
        drop_columns=["Unnamed: 0"],
        convert_geom=False,
    ):
        """
        get_csv: function for open and merge csv files on the object store

        Args:
        filenames (str): the names of the files, separated by comma.
            The pathname should be separated by ':'. For example, if you want to open
            the files data/file1 and data/file2, you should pass data:file1,data:file2.

        drop_columns (str): columns that you want to drop in the final file. It should be
            separated by column name. For example: test,data. Default is 'Unnamed: 0'

        columns (str): name and values of default columns to add to the the data.
            For example, if you want to add a column test with value 10 and a column data
            with value true, the value of columns should be test:10,data:true. Default is None.

        convert_geom (Optional(bool)): A flag that indicates if latitude and longitude will
            be converted to geometry

        Return:
            None
        """

        self.df = pd.DataFrame()
        for filename in filenames:
            filename = filename.replace(":", "/")
            url = f"{self.base_url}{filename}"

            data = pd.read_csv(url)

            for column in drop_columns:
                if column in data.columns:
                    data.drop(columns=column, inplace=True)
            if len(self.df) == 0:
                self.df = data
            else:
                merge_columns = list(set(self.df.columns) & set(data.columns))
                self.df = self.df.merge(data, how="outer", on=merge_columns)
        if columns:
            columns = columns.split(",")
            for column in columns:
                key, value = column.split(":")
                if value.lower() == "false":
                    value = False
                elif value.lower() == "true":
                    value = True
                self.df[key] = value

        self.df = self.df.fillna("")
        if convert_geom:
            self.df = gpd.GeoDataFrame(
                self.df,
                geometry=gpd.points_from_xy(
                    self.df["longitude"],
                    self.df["latitude"],
                    crs="EPSG:4326",
                ),
            )
            self.df.drop(columns=["latitude", "longitude"], inplace=True)
