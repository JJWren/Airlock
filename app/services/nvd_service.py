import nvdlib
from typing import List
from app.core.config import get_settings
from app.models.vulnerability import CVEData

# TODO: Finish this structure out.
# TODO: Remove these TODO comments once completed before you push your feature branch.
class NVDService:
    """Service to enrich SBOM artifacts with NIST vulnerability data."""

    def __init__(self):
        """Initializes the service with the federal NVD API Key."""
        self.settings = get_settings()
        self.api_key = self.settings.nvd_api_key

    def get_cves_by_cpe(self, cpe_string: str) -> List[CVEData]:
        """
        Queries NVD for a specific CPE and returns a list of CVEData objects.
        NVDLib handles the API 2.0 rate limits automatically when a key is provided.
        """
        # KEY WARNING: This should be implemented asynchronously. Utilize the Httpx package/library to accomplish this.

        # 1. Guardrail error if api key is missing
        # TODO: Implement guardrail with useful error message (throw exception/error): ValueError? ConfigurationError?

        # 2. Fetch raw data from NIST
        # TODO: nvdlib.searchCVE() is the api endpoint you will need to hit and feed the api key to
        # TODO: need an empty list for transforming the response objects into our CVEData objects
        # Should handle missing CVSS scores gracefully (set a default perhaps?)

        # 3. Map raw NVD objects to our Pydantic 'CVEData' contract
        # TODO: Need to:
        #  - parse and iterate through the CVEs from the NVD response object
        #  - transform each iteration of CVE objects into our CVEData objects
        #  - append those items to our empty list

        # TODO: return populated list of CVEData objects
        raise NotImplementedError("NVDService.get_cves_by_cpe is not implemented yet.")
