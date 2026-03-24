import asyncio, httpx, nvdlib
from typing import List
from app.core.config import get_settings
from app.core.logger import log
from app.models.vulnerability import CVEData


class NVDService:
    """Service to enrich SBOM artifacts with NIST vulnerability data."""

    def __init__(self):
        """Initializes the service with the federal NVD API Key."""
        self.settings = get_settings()
        self.api_key = self.settings.nvd_api_key
        self.base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
        self.headers = {
            "apiKey": self.api_key
        } if self.api_key else {}
        log.info("📡 NVD Service initialized.")

    async def get_cves_by_cpe(self, cpe_string: str) -> List[CVEData]:
        """
        Queries NVD for a specific CPE and returns a list of CVEData objects.
        NVDLib handles the API 2.0 rate limits automatically when a key is provided.
        """
        # A 0.6s delay ensures we never exceed 100 requests per minute
        await asyncio.sleep(0.6)

        if not self.api_key:
            log.error("❌ NVD Query aborted: API Key missing from configuration.")
            raise ValueError('API Key not provided or configured.')

        try:
            # We wrap the sync nvdlib call in a thread to keep the event loop alive
            raw_cves = await asyncio.to_thread(nvdlib.searchCVE, cpeName=cpe_string, key=self.api_key)
            results = self._process_nvdlib_results(raw_cves)
            return results
        except Exception as e:
            log.warning(f"⚠️ NVD CPE Search failed for {cpe_string}: {str(e)}")
            return []

    async def get_cves_by_keyword(self, package_name: str, version: str) -> List[CVEData]:
        """Search NVD by keyword when CPE matching fails."""
        await asyncio.sleep(0.6)

        if not self.api_key:
            log.error("❌ NVD Query aborted: API Key missing from configuration.")
            raise ValueError('API Key not provided or configured.')

        keyword = f"{package_name} {version}"
        params = {"keywordSearch": keyword}

        log.debug(f"🔍 Keyword Search: '{keyword}'")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.base_url,
                    headers=self.headers,
                    params=params,
                    timeout=30.0)
                if response.status_code != 200:
                    log.error(f"❌ NVD Keyword API error: {response.status_code} for {package_name}")
                    return []

                return NVDService._parse_nvd_response(response.json())
            except Exception as e:
                log.error(f"❌ NVD Keyword Connection error: {str(e)}")
                return []

    @staticmethod
    def _parse_nvd_response(data: dict) -> List[CVEData]:
        """Converts raw NIST JSON into our internal CVEData models."""
        vulnerabilities = []
        # Navigate the NIST 2.0 JSON structure
        vulnerabilities_list = data.get("vulnerabilities", [])

        for item in vulnerabilities_list:
            cve = item.get("cve", {})
            metrics = cve.get("metrics", {})

            # Use CVSS v3.1 severity if available
            cvss_v31_list = metrics.get("cvssMetricV31") or [{}]
            cvss_v31 = cvss_v31_list[0].get("cvssData", {})
            severity = cvss_v31.get("baseSeverity", "UNKNOWN")
            score = cvss_v31.get("baseScore", 0.0)

            descriptions_list = cve.get("descriptions") or [{}]
            description_value = descriptions_list[0].get("value", "No description available")

            vulnerabilities.append(CVEData(
                id=cve.get("id"),
                severity=severity,
                base_score=score,
                description=description_value,
                source_url=f"https://nvd.nist.gov/vuln/detail/{cve.get('id')}"
            ))

        count = len(data.get("vulnerabilities", []))
        if count > 0:
            log.success(f"📦 Keyword match found {count} potential issues.")
        return vulnerabilities

    @staticmethod
    def _process_nvdlib_results(raw_cves: list) -> List[CVEData]:
        """Maps raw NVDLib objects to the internal CVEData contract."""
        cve_list: List[CVEData] = []
        log.debug(f"⚙️  Processing {len(raw_cves)} raw records from NVDLib...")

        for cve in raw_cves:
            cvss_score = 0.0
            # NVDLib objects have specific attributes for different CVSS versions
            try:
                if hasattr(cve, 'v31score') and cve.v31score is not None:
                    cvss_score = float(cve.v31score)
                elif hasattr(cve, 'v30score') and cve.v30score is not None:
                    cvss_score = float(cve.v30score)
                elif hasattr(cve, 'v2score') and cve.v2score is not None:
                    cvss_score = float(cve.v2score)
            except (TypeError, ValueError):
                pass

            cve_data = CVEData(
                id=cve.id,
                severity=(
                        getattr(cve, 'v31severity', None) or
                        getattr(cve, 'v30severity', None) or
                        getattr(cve, 'v2severity', None) or
                        "UNKNOWN"
                ),
                base_score=cvss_score,
                description=cve.descriptions[0].value if cve.descriptions else "No description available.",
                source_url=cve.url,
            )
            cve_list.append(cve_data)

        if cve_list:
            log.success(f"🚩 Found {len(cve_list)} vulnerabilities via CPE.")
        else:
            log.info("✅ No vulnerabilities found for this CPE.")
        return cve_list
