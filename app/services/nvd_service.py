import asyncio
from typing import List
import nvdlib
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

    async def get_cves_by_cpe(self, cpe_string: str) -> List[CVEData]:
        """
        Queries NVD for a specific CPE and returns a list of CVEData objects.
        NVDLib handles the API 2.0 rate limits automatically when a key is provided.
        """
        # KEY WARNING: This should be implemented asynchronously. Utilize the Httpx package/library to accomplish this.

        # 1. Guardrail error if api key is missing
        # TODO: Implement guardrail with useful error message (throw exception/error): ValueError? ConfigurationError?
        if not self.api_key:
            raise ValueError('API Key not provided or configured.')

        # 2. Fetch raw data from NIST
        # TODO: nvdlib.searchCVE() is the api endpoint you will need to hit and feed the api key to
        # TODO: need an empty list for transforming the response objects into our CVEData objects
        # Should handle missing CVSS scores gracefully (set a default perhaps?)
        raw_cves = await asyncio.to_thread(nvdlib.searchCVE, cpeName=cpe_string, key=self.api_key)

        # 3. Map raw NVD objects to our Pydantic 'CVEData' contract
        # TODO: Need to:
        #  - parse and iterate through the CVEs from the NVD response object
        #  - transform each iteration of CVE objects into our CVEData objects
        #  - append those items to our empty list
        # TODO: return populated list of CVEData objects
        cve_list: List[CVEData] = []

        for cve in raw_cves:
            cvss_score = 0.0

            try:
                if hasattr(cve, 'v31score') and cve.v31score is not None:
                    cvss_score = float(cve.v31score)
                elif hasattr(cve, 'v30score') and cve.v30score is not None:
                    cvss_score = float(cve.v30score)
                elif hasattr(cve, 'v2score') and cve.v2score is not None:
                    cvss_score = float(cve.v2score)
            except (TypeError, ValueError):
                pass

            """
            cve_data = CVEData(
                id = cve.id,
                severity = cve.severity,
                base_score=cvss_score,
                description = cve.description[0].value if cve.description else "No description available.",
                source_url = cve.source_url)
            """
            cve_data = CVEData(
                id=cve.id,
                severity=cve.v31severity or cve.v30severity or cve.v2severity or "UNKNOWN",
                base_score=cvss_score,
                description=cve.descriptions[0].value if cve.descriptions else "No description available.",
                source_url=cve.url,
            )

            cve_list.append(cve_data)

        return cve_list
