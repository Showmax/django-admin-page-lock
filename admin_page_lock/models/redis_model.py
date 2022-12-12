from __future__ import unicode_literals

import datetime
import json
from collections import namedtuple

import smhasher
from redis import StrictRedis
from redis.exceptions import RedisError

from admin_page_lock.models.base_model import BasePageLockModel
from admin_page_lock.settings import REDIS_PREFIX, REDIS_SETTINGS, TIMEOUT

RedisSettings = namedtuple("RedisSettings", ["host", "port", "password", "timeout"])


class RedisPageLockModel(BasePageLockModel):
    @classmethod
    def _get_page_reference(cls, req):
        # Include `url parameters` to `page reference` in case
        # `URL_IGNORE_PARAMETERS` is set up to `False`.
        page_parameters = cls._get_page_url_parameters(req)
        page_url = cls._get_page_url(req)

        # Encode `url_parameters` and `url`.
        hex_url = hex(
            smhasher.murmur3_x64_128("{}{}".format(page_url, page_parameters))
        )

        # Return unique page reference that will be used as `redis key`.
        return "{}:{}".format(REDIS_PREFIX, hex_url)

    @classmethod
    def _get_redis_client(cls):
        redis_settings = cls._get_redis_settings()

        redis_client = StrictRedis(
            host=redis_settings.host,
            port=redis_settings.port,
            password=redis_settings.password,
            socket_timeout=redis_settings.timeout,
        )

        return redis_client

    @classmethod
    def _get_redis_settings(cls):
        # TODO(vstefka) add try block
        redis_settings = RedisSettings(
            REDIS_SETTINGS["host"],
            REDIS_SETTINGS["port"],
            REDIS_SETTINGS["password"],
            REDIS_SETTINGS["timeout"],
        )

        return redis_settings

    @classmethod
    def deactivate(cls, page_settings):
        # Deactivate page connection by deleting stored data for current page
        # in `Redis`.
        redis_client = page_settings["redis_client"]
        page_reference = page_settings["page_reference"]

        redis_client.delete(page_reference)

    @classmethod
    def get_page_settings(cls, req):
        page_settings = super(RedisPageLockModel, cls).get_page_settings(req)

        page_settings["page_reference"] = cls._get_page_reference(req)
        page_settings["redis_client"] = cls._get_redis_client()

        return page_settings

    @classmethod
    def get_data(cls, page_settings):
        # Get data from `Redis` for page defined by `page_reference`.
        redis_client = page_settings["redis_client"]
        page_reference = page_settings["page_reference"]

        try:
            data = redis_client.get(page_reference)
            data = json.loads(data)
        except (IndexError, RedisError, TypeError):
            return None

        data_to_return = {}
        for parameter_name, parameter_value in data.items():
            # Return parameters `locked_at` and `locked_out` as
            # `datetime.datetime` instances.
            if parameter_name in ["locked_at", "locked_out"]:
                parameter_value = datetime.datetime.strptime(
                    parameter_value, "%Y-%m-%d-%H-%M-%S"
                )
            data_to_return.update({parameter_name: parameter_value})

        return data_to_return

    @classmethod
    def set_data(cls, page_settings, data):
        page_reference = page_settings["page_reference"]
        redis_client = page_settings["redis_client"]

        data_to_store = {}
        for parameter_name, parameter_value in data.items():
            # Store `datetime.datetime` data in string format in Redis.
            if parameter_name in ["locked_at", "locked_out"]:
                parameter_value = parameter_value.strftime("%Y-%m-%d-%H-%M-%S")

            data_to_store.update({parameter_name: parameter_value})

        try:
            redis_client.set(
                page_reference,
                json.dumps(data_to_store),
                TIMEOUT,  # This deactives old records.
            )
        except RedisError:
            raise
