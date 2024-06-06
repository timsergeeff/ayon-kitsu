"""tests for endpoint 'api/addons/kitsu/{version}/push'
with entities of kitsu type: Project

$ poetry run pytest tests/test_push_project.py
"""

from pprint import pprint

import pytest

from . import mock_data
from .fixtures import (
    PAIR_PROJECT_CODE,
    PAIR_PROJECT_NAME,
    PROJECT_CODE,
    PROJECT_ID,
    PROJECT_NAME,
    api,
    kitsu_url,
    ensure_kitsu_server_setting,
)

from kitsu_mock import KitsuMock


def test_update_project_attrib(
    api, kitsu_url, ensure_kitsu_server_setting, monkeypatch
):
    """update project attrib based on kitsu"""

    entity = mock_data.projects[0]
    project_name = entity["name"]

    api.delete(f"/projects/{project_name}")
    assert not api.get_project(project_name)

    project_meta = {
        "code": entity["code"],
        "data": {"kitsuProjectId": entity["id"]},  # linked to kitsu entity
        "folderTypes": [{"name": "Folder"}],
        "taskTypes": [{"name": "Animation"}],
        "statuses": [{"name": "Todo"}],
    }

    # create the test project
    res = api.put(f"/projects/{project_name}", **project_meta)
    project = api.get_project(project_name)
    print(project["attrib"])

    # lets change the fps
    new_fps = 24.0 if project["attrib"]["fps"] == 25.0 else 25.0

    # change frameStart and frameEnd
    new_frame_start = 2 if project["attrib"]["frameStart"] == 1 else 1
    new_frame_end = 200 if project["attrib"]["frameEnd"] == 100 else 100

    attrib = {"fps": new_fps, "frameStart": new_frame_start, "frameEnd": new_frame_end}

    project = api.update_project(project_name, library=False, attrib=attrib)
    project = api.get_project(project_name)
    print(project)

    assert project["attrib"]["fps"] == new_fps
    assert project["attrib"]["frameStart"] == new_frame_start
    assert project["attrib"]["frameEnd"] == new_frame_end

    res = api.post(
        f"{kitsu_url}/push",
        project_name=entity["name"],
        entities=[entity],
        mock=True,
    )
    assert res.status_code == 200
    project = api.get_project(project_name)

    assert (
        project["attrib"]["fps"] != new_fps
    ), "fps should have been updated from kitsu"

    api.delete(f"/projects/{project_name}")
