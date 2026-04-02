import asyncio, os, tempfile
from app.core.logger import log
from app.services.syft_service import SyftService
from app.services.nvd_service import NVDService
from app.models.vulnerability import VulnerabilityReport


class CorrelationService:
    """Orchestrates SBOM generation and NVD vetting."""

    def __init__(self):
        self.syft_service = SyftService()
        self.nvd_service = NVDService()
        self.semaphore = asyncio.Semaphore(2) # Protects against NVD rate limits

    async def _vet_package(self, item: dict, target_severities: list) -> VulnerabilityReport | None:
        """Internal helper to vet a single package with rate-limit protection."""
        name = item.get("name")
        version = item.get("version")
        cpes = item.get("cpes", [])[:3]  # Using Syft's top 3 CPE guesses

        if not name or not version:
            return None

        async with self.semaphore:
            # Step 1: Attempt CPE-based vetting
            if cpes:
                for cpe_entry in cpes:
                    current_cpe = cpe_entry.get("cpe") if isinstance(cpe_entry, dict) else cpe_entry
                    try:
                        raw_findings = await self.nvd_service.get_cves_by_cpe(current_cpe)
                        if raw_findings:
                            filtered = [f for f in raw_findings if f.severity in target_severities]
                            if filtered:
                                return VulnerabilityReport(
                                    package_name=name,
                                    installed_version=version,
                                    cpe=current_cpe,
                                    vulnerabilities=filtered
                                )
                    except Exception as e:
                        log.error(f"❌ NVD Error for {name}: {str(e)}")

            # Step 2: Fallback to Keyword Search (Package Name + Version)
            try:
                keyword_findings = await self.nvd_service.get_cves_by_keyword(name, version)
                if keyword_findings:
                    filtered = [f for f in keyword_findings if f.severity in target_severities]
                    if filtered:
                        return VulnerabilityReport(
                            package_name=name,
                            installed_version=version,
                            cpe="NVD-KEYWORD-MATCH",
                            vulnerabilities=filtered
                        )
            except Exception as e:
                log.error(f"❌ NVD Keyword Error for {name}: {str(e)}")

        return None

    async def analyze_manifest_content(self, filename: str, content: str) -> tuple[list[VulnerabilityReport], int]:
        """Stages and scans an uploaded manifest file."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, filename), "w") as f: f.write(content)
            raw = await asyncio.to_thread(self.syft_service.generate_sbom, tmp)
            return await self._process_artifacts(raw.get("artifacts", []))

    async def scan_directory(self, target_path: str) -> tuple[list[VulnerabilityReport], int]:
        """Scans a local directory path."""
        raw = await asyncio.to_thread(self.syft_service.generate_sbom, target_path)
        return await self._process_artifacts(raw.get("artifacts", []))

    async def _process_artifacts(self, artifacts: list) -> tuple[list[VulnerabilityReport], int]:
        """Internal helper to deduplicate and vet SBOM artifacts."""
        unique = {(a.get("name"), a.get("version")): a for a in artifacts}
        unique_list = list(unique.values())
        tasks = [self._vet_package(i, ["HIGH", "CRITICAL"]) for i in unique_list]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None], len(unique_list)
