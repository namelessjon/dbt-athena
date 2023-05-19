import boto3
import pytest
from tests.unit.constants import AWS_REGION, DATA_CATALOG_NAME, DATABASE_NAME

from dbt.adapters.athena.lakeformation import LfTagsConfig, LfTagsManager
from dbt.adapters.athena.relation import AthenaRelation


# TODO: add more tests for lakeformation once moto library implements required methods:
# https://docs.getmoto.org/en/4.1.9/docs/services/lakeformation.html
# get_resource_lf_tags
class TestLfTagsManager:
    @pytest.mark.parametrize(
        "response,columns,lf_tags,verb,expected",
        [
            pytest.param(
                {
                    "Failures": [
                        {
                            "LFTag": {"CatalogId": "test_catalog", "TagKey": "test_key", "TagValues": ["test_values"]},
                            "Error": {"ErrorCode": "test_code", "ErrorMessage": "test_err_msg"},
                        }
                    ]
                },
                ["column1", "column2"],
                {"tag_key": "tag_value"},
                "add",
                None,
                id="lf_tag error",
                marks=pytest.mark.xfail,
            ),
            pytest.param(
                {"Failures": []},
                None,
                {"tag_key": "tag_value"},
                "add",
                "Success: add LF tags: {'tag_key': 'tag_value'} to test_dbt_athena.tbl_name",
                id="add lf_tag",
            ),
            pytest.param(
                {"Failures": []},
                None,
                {"tag_key": "tag_value"},
                "remove",
                "Success: remove LF tags: {'tag_key': 'tag_value'} to test_dbt_athena.tbl_name",
                id="remove lf_tag",
            ),
            pytest.param(
                {"Failures": []},
                ["c1", "c2"],
                {"tag_key": "tag_value"},
                "add",
                "Success: add LF tags: {'tag_key': 'tag_value'} to test_dbt_athena.tbl_name for columns ['c1', 'c2']",
                id="lf_tag database table and columns",
            ),
        ],
    )
    def test__parse_lf_response(self, response, columns, lf_tags, verb, expected):
        relation = AthenaRelation.create(database=DATA_CATALOG_NAME, schema=DATABASE_NAME, identifier="tbl_name")
        lf_client = boto3.client("lakeformation", region_name=AWS_REGION)
        manager = LfTagsManager(lf_client, relation, LfTagsConfig())
        assert manager._parse_lf_response(response, columns, lf_tags, verb) == expected