import asyncio, time
from typing import List
from app.core.logger import log
from app.services.syft_service import SyftService
from app.services.nvd_service import NVDService
from app.models.vulnerability import VulnerabilityReport, CVEData


class CorrelationService:
    """Orchestrates the SBOM generation and vulnerability enrichment."""

    def __init__(self):
        # These services automatically pull their paths/keys from get_settings()
        self.syft_service = SyftService()
        self.nvd_service = NVDService()

        # Limit to 2 concurrent NVD requests to be safe with rate limits
        self.semaphore = asyncio.Semaphore(2)

        log.info("📡 Correlation Service initialized.")

    async def _vet_package(self, item: dict, target_severities: list) -> VulnerabilityReport | None:
        """Internal helper to vet a single package with rate-limit protection."""
        name = item.get("name")
        version = item.get("version")

        # Step 1: Try ALL CPEs Syft provides
        cpes = item.get("cpes", [])

        if not cpes:
            log.debug(f"⏭️  Skipping {name}: No CPEs provided by scanner.")
            return None

        async with self.semaphore: # Ensures we don't spam the NVD
            # First Attempt: Use CPEs
            for cpe_entry in cpes:
                current_cpe = cpe_entry.get("cpe") if isinstance(cpe_entry, dict) else cpe_entry
                log.debug(f"🔍 Vetting {name} via {current_cpe}...")

                try:
                    raw_findings = await self.nvd_service.get_cves_by_cpe(current_cpe)
                    if raw_findings:
                        filtered = [f for f in raw_findings if f.severity in target_severities]
                        if filtered:
                            log.success(f"🚩 {name}: {len(filtered)} {target_severities} issues found.")
                            return VulnerabilityReport(
                                package_name=name,
                                installed_version=version,
                                cpe=current_cpe,
                                vulnerabilities=filtered
                            )
                except Exception as e:
                    log.error(f"❌ NVD Error for {name}: {str(e)}")

            # Step 2: Fallback - Search NVD by Keyword (Package Name + Version)
            # This catches cases where Syft's CPE guesses are all "off-target"
            log.info(f"🔄 CPEs failed for {name}, trying Keyword Search...")
            try:
                keyword_findings = await self.nvd_service.get_cves_by_keyword(name, version)
                if keyword_findings:
                    filtered = [f for f in keyword_findings if f.severity in target_severities]
                    if filtered:
                        log.success(f"🚩 {name}: Found {len(filtered)} issues via Keyword Search!")
                        return VulnerabilityReport(
                            package_name=name,
                            installed_version=version,
                            cpe="NVD-KEYWORD-MATCH",
                            vulnerabilities=filtered
                        )
                else:
                    log.debug(f"ℹ️  {name}: No {target_severities} issues found via Keyword.")
            except Exception as e:
                log.error(f"❌ NVD Keyword Error for {name}: {str(e)}")
            return None

    async def run_full_scan(self, target_path: str) -> list[VulnerabilityReport] | None:
        """
        1. Runs Syft to generate the SBOM.
        2. Iterates through artifacts that have CPEs.
        3. Queries NVD for vulnerabilities.
        4. Returns a list of correlated reports.
        """
        start_time = time.perf_counter()
        log.info(f"\n🚀 Starting full scan for: {target_path}")

        # Step 1: Syft Scan
        syft_start = time.perf_counter()
        raw_sbom = await asyncio.to_thread(self.syft_service.generate_sbom, target_path)
        log.info(f"⏱️ Syft Scan Complete: {time.perf_counter() - syft_start:.2f}s")

        artifacts = raw_sbom.get("artifacts", [])
        log.info(f"📦 Found {len(artifacts)} packages to vet.")

        target_severities = ["HIGH", "CRITICAL"]

        # Step 2: Parallel Vetting
        tasks = [self._vet_package(item, target_severities) for item in artifacts]
        results = await asyncio.gather(*tasks)

        # Filter out None results
        reports = [r for r in results if r is not None]

        log.info(f"✅ Airlock Scan Complete in {time.perf_counter() - start_time:.2f}s")
        log.info(f"📊 Summary: {len(reports)}/{len(artifacts)} packages found to be vulnerable.")
        return reports