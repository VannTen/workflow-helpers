#!/usr/bin/env python3
# workflow-helpers
# Copyright(C) 2022 Kevin Postlethwait
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""This script sends all webhooks in a directory, each is represented by a JSON object."""

import json
import logging
import os

from kubernetes import kubernetes as k8

import requests

k8.config.load_kube_config()
core_api = k8.client.CoreV1Api()

dir = os.environ["WEBHOOK_DIR"]
document_id = os.environ["DOCUMENT_ID"]
secret_namespace = os.environ["THOTH_BACKEND_NAMESPACE"]

_LOGGER = logging.getLogger("thoth.send_webhooks")

for f_name in os.listdir(dir):
    with open(os.path.join(dir, f_name), "r") as f:
        webhook = json.load(f)
    contents = {
        "client_data": webhook["client_data"],
        "document_id": document_id,
    }
    headers = {"Authorization": webhook["Authorization"]}
    try:
        requests.post(url=webhook["callback_url"], data=contents, headers=headers)
    except Exception as e:
        _LOGGER.exception(e)

core_api.delete_namespaced_secret(name=f"callback-{document_id}", namespace=secret_namespace)
