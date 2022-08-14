import logging
import time
import xml.etree.ElementTree as Et

import requests
from ratelimit import limits, sleep_and_retry

import aligni.datatypes
import aligni.endpoints

# Aligni has a rate limit of 30 calls per minute
CALLS = 4
RATE_LIMIT = 10


@sleep_and_retry
@limits(calls=CALLS, period=RATE_LIMIT)
def check_limit():
    """Empty function just to check for calls to API and enforce ratelimit"""
    return


def session_request_template(request_function, request_function_str, sitename, apikey):
    def session_request(endpoint, data=None, params=None):
        check_limit()
        if data is None:
            logging.debug(
                request_function_str,
                ": https://{}.aligni.com/api/v2/{}/{}".format(
                    sitename, apikey, endpoint
                ),
            )
        else:
            logging.debug(
                request_function_str,
                ": https://%s.aligni.com/api/v2/%s/%s data=%s"
                % (sitename, apikey, endpoint, data),
            )

        max_attempts = 3
        attempts = 0
        while attempts < max_attempts:
            r = request_function(
                f"https://{sitename}.aligni.com/api/v2/{apikey}/{endpoint}",
                data=data,
                params=params,
            )

            if r.status_code == 429:
                # We activily limit requests but rate limit errors still occur occasionally.
                logging.warning("Aligni Rate Limit Exceeded, retrying in 5 mins")
                time.sleep(5 * 60)
                attempts = attempts + 1
            else:
                break

        logging.debug(
            request_function_str, " Status: %i Response: %s", r.status_code, r.text
        )

        # Check if the request was successful and raise an exception if not.
        if r.status_code == 400:
            # Note that a 'Bad Request' error can be raised if the 'id' or 'name'
            # of the new item already exists on the server.
            raise requests.ConnectionError(r.reason)
        elif r.status_code == 404:
            # Item not found.
            return None
        elif r.status_code == 429:
            raise requests.ConnectionError(
                "Aligni Rate Limit Exceeded - max retries exhausted"
            )
        elif not r.text or r.text.isspace():
            return None
        return Et.fromstring(r.text)

    return session_request


class API:
    """Aligni API handler for Python"""

    def __init__(self, sitename, apikey):
        self.sitename = sitename
        self.apikey = apikey
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/xml", "Content-Type": "application/xml"}
        )

        # Define requestion functions (GET, PUT, POST & DELETE)
        self.__host_get = session_request_template(
            self.session.get, "GET", self.sitename, self.apikey
        )
        self.__host_put = session_request_template(
            self.session.put, "PUT", self.sitename, self.apikey
        )
        self.__host_post = session_request_template(
            self.session.post, "POST", self.sitename, self.apikey
        )
        self.__host_delete = session_request_template(
            self.session.delete, "DELETE", self.sitename, self.apikey
        )

        # Define all the supported endpoints based on the "type".
        self.manufacturers = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.Manufacturer,
            "manufacturer/{}",
        )
        self.vendors = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.Vendor,
            "vendor/{}",
        )
        self.parttypes = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.PartType,
            "parttype/{}",
        )
        self.parameters = aligni.endpoints._BaseList(
            self.__host_get,
            None,
            None,
            None,
            aligni.datatypes.PartParameterField,
            "part_parameter_field/{}",
        )
        self.units = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.Unit,
            "unit/{}",
        )
        self.parts = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.Part,
            "part/{}",
        )
        self.inventorylocation = aligni.endpoints._BaseList(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.InventoryLocation,
            "inventory_location/{}",
        )
        self.partrevisions = aligni.endpoints._PartRevision(
            self.__host_get,
            self.__host_post,
            self.__host_delete,
            aligni.datatypes.PartRevision,
            "parts/{}/revisions/{}",
        )
        self.unitconversion = aligni.endpoints._BaseCreateDelete(
            self.__host_post,
            self.__host_delete,
            aligni.datatypes.UnitConversion,
            "unit_conversion/{}",
        )
        self.quote = aligni.endpoints._BaseCreateDelete(
            self.__host_post, self.__host_delete, aligni.datatypes.Quote, "quote/{}"
        )
        self.vendorpartnumber = aligni.endpoints._BaseCreateDelete(
            self.__host_post,
            self.__host_delete,
            aligni.datatypes.VendorPartNumber,
            "vendor_partnumber/{}",
        )
        self.inventorysublocation = aligni.endpoints._BaseCreateGetDelete(
            get_cmd=self.__host_get,
            post_cmd=self.__host_post,
            delete_cmd=self.__host_delete,
            aligni_type=aligni.datatypes.InventorySublocation,
            aligni_endpoint="inventory_sublocation/{}",
        )
        self.partinventoryunits = aligni.endpoints._PartInventory(
            self.__host_get,
            self.__host_post,
            self.__host_put,
            self.__host_delete,
            aligni.datatypes.InventoryUnit,
            "parts/{}/inventory_units/{}",
        )
        self.linecards = aligni.endpoints._Linecard(
            self.__host_post,
            self.__host_delete,
            aligni.datatypes.LineCard,
            "linecard?vendor_id={}&manufacturer_id={}",
        )
