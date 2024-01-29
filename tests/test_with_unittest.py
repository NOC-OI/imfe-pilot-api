# pylint: disable=line-too-long
# pylint: disable=unnecessary-pass

"""
Pytest codes for the API endpoints It is based on the class TryTesting(TestCase).
To run the tests, you need to run make test
"""

import os
from unittest import TestCase

import jwt

from api.v1.calc import calc_results
from api.v1.data import open_csv  # , open_stac
from api.v1.user import create_user, get_signed_url_by_token

os.environ["ENV"] = "DEV"


class TryTesting(TestCase):
    """
    Class TryTesting: class to perform the tests.

    The following test are being performed:
            - test_open_csv_add_columns: open csv file and add columns to it
            - test_open_csv: verify if a csv file can be open correctly
            - test_open_csv_skip_lines: verify if skip lines is getting the
            correct parts of the csv file
            - test_open_csv_clip: verify if a csv file can be open correctly. And then,
            verify if the file can be clipped given a bbox value
            - test_calc_count: test the count calculation and test get bbox
            - test_calc_unique: test the unique calculation
            - test_calc_agg: test the agg calculation
            - test_calc_organism: test the organism calculation by density
            - test_calc_organism_number: test the organism calculation by number
            - test_calc_biodiversity1: test the biodiversity1 calculation
            - test_calc_biodiversity2: test the biodiversity2 calculation
            - test_calc_biodiversity3: test the biodiversity3 calculation
            - test_calc_biodiversity4: test the biodiversity4 calculation
            - test_calc_biodiversity5: test the biodiversity5 calculation
            - test_calc_agg_density_number: test the agg calculation without first and
            with density and number
            - test_open_stac: verify if a stac file can be open correctly
    """

    def test_open_csv_add_columns(self):
        """
        test_open_csv_add_columns: open csv file and add columns to it
        """

        value = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_annotation_summary",
            columns="ok:true,ok1:false,teste:10",
        )
        assert isinstance(value, list)
        assert "ok" in list(value[0].keys())
        assert "ok1" in list(value[0].keys())
        assert "teste" in list(value[0].keys())
        assert value[0]["ok"]
        assert not value[0]["ok1"]
        assert value[0]["teste"] == "10"

    def test_calc_agg_density_number(self):
        """
        test_calc_agg_density_number: test the agg calculation without first and
            with density and number
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="agg",
            crs="epsg:4326",
            extension="csv",
            agg_columns="density:,count:area_seabed_m2",
            calc_columns="habitat",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["habitat"]
        assert list(value["habitat"].keys()) == ["Types"]
        assert isinstance(value["habitat"]["Types"], list)
        assert "salmacina_dysteri" in list(value["habitat"]["Types"][0].keys())
        assert "area_seabed_m2" not in list(value["habitat"]["Types"][0].keys())
        assert "Number" in list(value["habitat"]["Types"][0].keys())
        assert "habitatImage" not in list(value["habitat"]["Types"][0].keys())

    def test_open_csv(self):
        """
        test_open_csv: verify if a csv file can be open correctly
        """

        value = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_annotation_summary,layers:seabed_images:hf2012:HF2012_other_data"
        )
        assert isinstance(value, list)
        assert len(value) == 1216
        assert isinstance(value[0], dict)
        assert list(value[0].keys()) == [
            "FileName",
            "antedon",
            "anthozoa",
            "anthozoa_01",
            "anthozoa_03",
            "anthozoa_05",
            "anthozoa_06",
            "anthozoa_07",
            "anthozoa_08",
            "anthozoa_11",
            "anthozoa_16",
            "anthozoa_19",
            "anthozoa_24",
            "anthozoa_34",
            "anthozoa_39",
            "asterias_rubens",
            "asteroid_01",
            "asteroid_07",
            "asteroidea",
            "astropecten_irregularis",
            "axinellidae",
            "bolocera",
            "bryozoa_01",
            "callionymus",
            "caryophyllia_smithii",
            "cerianthid_01",
            "cerianthid_03",
            "echinoid_01",
            "echinoidea",
            "echinus_esculentus",
            "eledone_02",
            "eledone_cirrhosa",
            "fish",
            "fish_10",
            "flatfish",
            "gadidae",
            "gadiforme_09",
            "gaidropsarus_vulgaris",
            "galeus",
            "hippoglossoides_platessoides",
            "hydroid_01",
            "inachidae_01",
            "inachidae_02",
            "INDETERMINATE",
            "indeterminate_29",
            "indeterminate_36",
            "lepidorhombus_whiffiagonis",
            "leucoraja_naevus",
            "liocarcinus",
            "lithodes_maja",
            "luidia_ciliaris",
            "luidia_sarsii",
            "marthasterias_glacialis",
            "microchirus_variegatus",
            "munida",
            "ophiuroid_01",
            "ophiuroid_02",
            "paguridae_01",
            "paguridae_02",
            "parazoanthus",
            "pentapora_foliacea",
            "porania_pulvillus",
            "porcellanidae",
            "porella",
            "porifera_02",
            "porifera_03",
            "porifera_20",
            "porifera_22",
            "porifera_23",
            "porifera_24",
            "porifera_25",
            "rajidae_01",
            "reteporella",
            "salmacina_dysteri",
            "scyliorhinus_canicula",
            "squid",
            "stichastrella_rosea",
            "urticina",
            "id",
            "Substratum",
            "Habitat",
            "Latitude",
            "Longitude",
            "Area_seabed_m2",
            "FileFormat",
        ]

    def test_open_csv_skip_lines(self):
        """
        test_open_csv_skip_lines: verify if skip lines is getting the correct parts of the csv file
        """

        value = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_annotation_summary",
        )

        value_header = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_annotation_summary",
            skip_lines=1,
        )

        value_tail = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_annotation_summary",
            skip_lines=-1,
        )
        assert isinstance(value_header, list)
        assert isinstance(value, list)
        assert isinstance(value_tail, list)

        assert len(value) > len(value_tail)
        assert len(value) > len(value_header)
        assert len(value_tail) == len(value_header)
        assert value[0] != value_header[0]
        assert value[0] == value_tail[0]
        assert value[-1] != value_tail[0]

    def test_open_csv_clip(self):
        """
        test_open_csv_clip: verify if a csv file can be open correctly. And then,
        test if the file can be clipped given a bbox value
        """

        value = open_csv(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            bbox="-10,50.36,5,50.37",
            crs="epsg:4326",
            lat_lon_columns="latitude,longitude",
        )
        assert isinstance(value, list)
        assert len(value) == 656
        assert isinstance(value[0], dict)
        part_list = [
            "filename",
            "id_image",
            "latitude",
            "longitude",
            "area_seabed_m2",
            "substratum",
        ]
        assert set(part_list).issubset(list(value[0].keys()))

    def test_calc_count(self):
        """
        test_calc_count: test the count calculation and test get bbox
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="count",
            crs="epsg:4326",
            extension="csv",
            calc_columns="habitat",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["habitat"]
        assert list(value["habitat"].keys()) == ["Number"]
        assert isinstance(value["habitat"]["Number"], list)

        value_bbox = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="count",
            crs="epsg:4326",
            extension="csv",
            calc_columns="habitat",
            bbox="-10,50.3665,5,50.3666",
        )

        assert isinstance(value_bbox, dict)
        assert list(value_bbox.keys()) == ["habitat"]
        assert list(value_bbox["habitat"].keys()) == ["Number"]
        assert isinstance(value_bbox["habitat"]["Number"], list)
        assert value_bbox["habitat"]["Number"][0] < value["habitat"]["Number"][0]

    def test_calc_unique(self):
        """
        test_calc_unique: test the unique calculation
        """

        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="unique",
            crs="epsg:4326",
            extension="csv",
            calc_columns="habitat",
            all_columns=True,
        )
        assert isinstance(value, dict)
        assert "habitat" in list(value.keys())

    def test_calc_agg(self):
        """
        test_calc_agg: test the agg calculation
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="agg",
            crs="epsg:4326",
            extension="csv",
            agg_columns="first:habitatImage",
            calc_columns="habitat",
        )
        assert isinstance(value, dict)
        assert list(value.keys()) == ["habitat"]
        assert list(value["habitat"].keys()) == ["Types"]
        assert isinstance(value["habitat"]["Types"], list)
        assert list(value["habitat"]["Types"][0].keys()) == ["habitat", "habitatImage"]

    def test_calc_organism(self):
        """
        test_calc_organism: test the organism calculation by density
        """

        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts,layers:seabed_images:jncc:JNCC_CEND1012_otherdata",
            calc="organism",
            crs="epsg:4326",
            extension="csv",
            exclude_index=True,
            agg_columns="first:filename,first:fileformat,sum:pentapora_foliacea,density:area_seabed_m2",
            calc_columns="pentapora_foliacea",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["pentapora_foliacea"]
        assert list(value["pentapora_foliacea"].keys()) == ["Information"]
        assert isinstance(value["pentapora_foliacea"]["Information"], list)
        assert list(value["pentapora_foliacea"]["Information"][0].keys()) == [
            "filename",
            "fileformat",
            "Density (individuals ha-1)",
            "Number of Specimens",
        ]

    def test_calc_organism_number(self):
        """
        test_calc_organism_number: test the organism calculation by number
        """

        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_otherdata,layers:seabed_images:hf2012:HF2012_alltile_counts,layers:seabed_images:jncc:JNCC_CEND1012_otherdata",
            calc="organism",
            crs="epsg:4326",
            extension="csv",
            exclude_index=True,
            agg_columns="first:filename,first:fileformat,sum:pentapora_foliacea",
            calc_columns="pentapora_foliacea",
        )
        assert isinstance(value, dict)
        assert list(value.keys()) == ["pentapora_foliacea"]
        assert list(value["pentapora_foliacea"].keys()) == ["Information"]
        assert isinstance(value["pentapora_foliacea"]["Information"], list)
        assert list(value["pentapora_foliacea"]["Information"][0].keys()) == [
            "filename",
            "fileformat",
            "Number",
        ]

    def test_calc_biodiversity1(self):
        """
        test_calc_biodiversity1: test the biodiversity1 calculation
        """

        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_SU",
            calc="biodiversity1",
            calc_columns="substratum",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["substratum"]
        assert list(value["substratum"].keys()) == ["Types"]
        assert isinstance(value["substratum"]["Types"], list)
        assert list(value["substratum"]["Types"][0].keys()) == [
            "substratum",
            "Density (individuals m-2)",
        ]

    def test_calc_biodiversity2(self):
        """
        test_calc_biodiversity2: test the biodiversity2 calculation
        """

        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_alltile_counts",
            calc="biodiversity2",
            calc_columns="biodiversity",
        )
        assert isinstance(value, dict)
        assert list(value.keys()) == ["biodiversity"]
        assert list(value["biodiversity"].keys()) == ["Number of morphotypes"]
        assert isinstance(value["biodiversity"]["Number of morphotypes"], list)
        assert isinstance(value["biodiversity"]["Number of morphotypes"][0], int)

    def test_calc_biodiversity3(self):
        """
        test_calc_biodiversity3: test the biodiversity3 calculation
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_SU",
            calc="biodiversity3",
            calc_columns="substratum",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["substratum"]
        assert list(value["substratum"].keys()) == ["Types"]
        assert isinstance(value["substratum"]["Types"], list)
        assert list(value["substratum"]["Types"][0].keys()) == ["substratum", "Number"]

    def test_calc_biodiversity4(self):
        """
        test_calc_biodiversity4: test the biodiversity4 calculation
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_SU",
            calc="biodiversity4",
            calc_columns="substratum",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["substratum"]
        assert list(value["substratum"].keys()) == ["Types"]
        assert isinstance(value["substratum"]["Types"], list)
        assert list(value["substratum"]["Types"][0].keys()) == ["substratum", "Result"]

    def test_calc_biodiversity5(self):
        """
        test_calc_biodiversity5: test the biodiversity5 calculation
        """
        value = calc_results(
            filenames="layers:seabed_images:hf2012:HF2012_SU",
            calc="biodiversity5",
            calc_columns="substratum",
        )

        assert isinstance(value, dict)
        assert list(value.keys()) == ["substratum"]
        assert list(value["substratum"].keys()) == ["Types"]
        assert isinstance(value["substratum"]["Types"], list)
        assert list(value["substratum"]["Types"][0].keys()) == ["substratum", "Result"]

    def test_for_user_create(self):
        """
        test_for_user_create
        """
        token = create_user(code="XXXX", state="orcid")
        user = jwt.decode(jwt=token, key="haig-fras", algorithms=["HS256"])
        assert user["name"] == "XXXX"
        assert user["orcid"] == "0000-0000-0000-0000"
        assert user["access"] == 1

    def test_for_not_user_create(self):
        """
        test_for_user_create
        """
        token = create_user(code="XXX1", state="orcid")
        user = jwt.decode(jwt=token, key="haig-fras", algorithms=["HS256"])
        assert user["name"] == "XXX1"
        assert user["orcid"] == "0000-0000-0000-0001"
        assert user["access"] == 0

    # def test_for_signed_url(self):
    #     """
    #     test_for_signed_url
    #     """
    #     token = create_user(code="XXXX", state="orcid")
    #     filenames = get_signed_url_by_token(token)

    #     assert isinstance(filenames, dict)
    #     assert len(filenames.keys()) >= 2

    def test_for_not_signed_url(self):
        """
        test_for_not_signed_url
        """
        token = "QQQQQ"
        filenames = ""
        filenames = get_signed_url_by_token(token)
        assert filenames == ""
