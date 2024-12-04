import requests
import polars as pl
from logging import getLogger
from requests.adapters import HTTPAdapter
from .lizard_types import LizardEndpoint
from .lizard_errors import LizardPOSTError, LizardGETError, InvalidUrlError

logger = getLogger(__name__)


class LizardRequests:
    def __init__(self, session: requests.Session, base_url: str) -> None:
        if not base_url.endswith(".lizard.net/api/v4"):
            raise InvalidUrlError("Base url should end with: .lizard.net/api/v4")

        self.api_base_url = base_url
        self.session = session
        adapter = HTTPAdapter(pool_connections=5, pool_maxsize=5)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self._test_connection()

    def _test_connection(self):
        r = self.session.get(self.api_base_url)
        r.raise_for_status

    def post_observationtype(self, dict: dict) -> requests.Response:
        """post an observation-type based on the dictionary"""
        url = f"{self.api_base_url}/observationtypes/"
        res = self.session.post(url, json=dict, timeout=15)
        res.raise_for_status()
        return res

    def get_observationtype(self, params: dict) -> requests.Response:
        """Get all observation-type based on the parameters provided"""
        url = f"{self.api_base_url}/observationtypes/"
        res = self.session.get(url, params=params, timeout=15)
        res.raise_for_status()
        return res

    def get_observationtype_id(self, query: str) -> str | None:
        """Looks up an object based on a query.
        If no or more than 1 results are found, None is returned.
        """
        url = f"{self.api_base_url}/observationtypes/?{query}"
        try:
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            count = r.json()["count"]

            if count == 1:
                id = r.json()["results"][0]["id"]
                logger.info(f"Observationtypes found with uuid: {id}")
                return id

            if count == 0:
                logger.warning("No observationtypes was found.")
                return None

            if count > 2:
                logger.warning("More than 1 observationtypes were found.")
                return None

        except Exception as e:
            raise LizardGETError(
                f"Failed to get observationtypes data from Lizard: {e}"
            )

    def get_lizard_objects(self, endpoint: LizardEndpoint, query: str) -> str | None:
        """Send a get request to Lizard based on the endpoint and possibly a custom query."""
        url = f"{self.api_base_url}/{endpoint}/?{query}"
        try:
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            count = r.json()["count"]

            if count == 0:
                logger.warning(f"No {endpoint} was found.")
                return None

            return r.json()["results"]

        except Exception as e:
            raise LizardGETError(f"Failed to get {endpoint} data from Lizard: {e}")

    def get_lizard_object_uuid(
        self, endpoint: LizardEndpoint, query: str
    ) -> list[str] | str | None:
        """
        Looks up an object based on a query.
        Returns uuid on exact match, None on no match, and the list of uuids on the first page for more than 1 match.
        """
        url = f"{self.api_base_url}/{endpoint}/?{query}"
        try:
            r = self.session.get(url, timeout=10)
            r.raise_for_status()
            count = r.json()["count"]

            if count == 1:
                uuid = r.json()["results"][0]["uuid"]
                logger.info(f"{endpoint} found with uuid: {uuid}")
                return uuid

            if count == 0:
                logger.warning(f"No {endpoint} was found.")
                return None

            if count > 2:
                results_df = pl.DataFrame(r.json()["results"])
                uuids = results_df.select("uuid").to_series(0).to_list()
                return uuids

        except Exception as e:
            raise LizardGETError(f"Failed to get {endpoint} data from Lizard: {e}")

    def post_lizard_location(self, data: dict) -> str | None:
        location_url = f"{self.api_base_url}/locations/"
        try:
            r = self.session.post(url=location_url, json=data, timeout=10)
            r.raise_for_status()
            uuid = r.json()["uuid"]
            logger.info(f"A location was successfully postd with uuid: {uuid}")
            return uuid

        except Exception as e:
            raise LizardPOSTError(f"Failed to post location data to Lizard: {e}")

    def post_lizard_timeserie(
        self,
        data: dict,
    ) -> requests.Response:
        """Does a POST on the LIzard timeserie endpoint. Returns the uuid of the postd Timeseries"""
        url = f"{self.api_base_url}/timeseries/"
        try:
            r = self.session.post(url, json=data, timeout=10)
            r.raise_for_status()
            logger.info("A timeserie was successfully posted.")
            return r

        except Exception as e:
            raise LizardPOSTError(f"Failed to post timeseries data to Lizard: {e}")

    def post_timeserie_events(
        self, timeserie_uuid: str, event_data: list[dict[str, str]]
    ) -> requests.Response:
        url = f"{self.api_base_url}/timeseries/{timeserie_uuid}/events/"

        try:
            r = self.session.post(url, json=event_data, timeout=10)
            r.raise_for_status()
            logger.info(
                f"Event data posted successfully to timeserie with uuid: {timeserie_uuid}"
            )
            return r

        except Exception as e:
            raise LizardPOSTError(f"Failed to post event data to Lizard: {e}")

    def post_to_bulk(self, bulk_data: list[dict]) -> requests.Response:
        url = f"{self.api_base_url}/timeseries/events/"
        try:
            r = self.session.post(url, json=bulk_data, timeout=30)
            r.raise_for_status()
            return r
        except Exception as e:
            raise LizardPOSTError(f"Failed to post event data to Lizard: {e}")

    def get_rastersource_uuid(self, name: str) -> str:
        rastersource_url = f"{self.api_base_url}/rastersources/?name={name}"
        try:
            r = self.session.get(url=rastersource_url, timeout=10)
            r.raise_for_status()
            if r.json()["count"] == 1:
                return r.json()["results"][0]["uuid"]
            else:
                return None
        except Exception as e:
            raise LizardGETError(f"Failed to get rastersource from Lizard: {e}")

    def post_rastersource(self, rastersource_dict: dict) -> requests.Response:
        rastersource_url = f"{self.api_base_url}/rastersources/"
        try:
            r = self.session.post(
                url=rastersource_url, json=rastersource_dict, timeout=30
            )
            r.raise_for_status()
            return r

        except Exception as e:
            raise LizardPOSTError(f"Failed to post rastersource to Lizard: {e}")

    def get_raster_uuid(self, name: str) -> str:
        raster_url = f"{self.api_base_url}/rasters/?name={name}"
        try:
            r = self.session.get(url=raster_url, timeout=30)
            r.raise_for_status()
            if r.json()["count"] == 1:
                return r.json()["results"][0]["uuid"]
            else:
                return None

        except Exception as e:
            raise LizardGETError(f"Failed to get rastersource from Lizard: {e}")

    def post_raster(self, raster_dict: dict) -> requests.Response:
        """Post a raster"""
        raster_url = f"{self.api_base_url}/rasters/"
        try:
            r = self.session.post(url=raster_url, json=raster_dict, timeout=30)
            r.raise_for_status()
            return r

        except Exception as e:
            raise LizardPOSTError(f"Failed to post rastersource to Lizard: {e}")

    def post_tif_to_lizard(
        self, filepath: str, rastersource_uuid: str, zulu_datetime: str
    ) -> requests.Response:
        """Posts a tif file to Lizard."""
        url = f"{self.api_base_url}/rastersources/{rastersource_uuid}/data/"
        try:
            with open(filepath, "rb") as file:
                openfile = {"file": file}
                data = {"timestamp": zulu_datetime}

                headers = self.session.headers.copy()
                headers.pop("Content-Type")
                self.session.headers = headers
                r = self.session.post(
                    url,
                    data=data,
                    files=openfile,
                    timeout=10,
                )
                r.raise_for_status()
                logger.info(
                    f"TIF file posted successfully to rastersource with uuid: {rastersource_uuid}"
                )
                return r

        except Exception as e:
            raise LizardPOSTError(f"Failed to post TIF file to Lizard: {e}")

    def check_task_status(self, task_uuid: str) -> dict:
        """
        Checks the status of all tasks provided.

        Returns
        -
        """
        response = self.session.get(
            f"{self.api_base_url}/tasks/?uuid_in={task_uuid}", timeout=10
        )
        response.raise_for_status()
        status = response.json().get("status", "UNKNOWN")
        return status
