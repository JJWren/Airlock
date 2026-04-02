export const mockScanResult = {
  summary: {
    total_packages: 5,
    vulnerable_packages: 3,
    critical_count: 4,
    high_count: 1
  },
  findings: [
    {
      package_name: "jinja2",
      installed_version: "2.10",
      cpe: "NVD-KEYWORD-MATCH",
      vulnerabilities: [
        {
          id: "CVE-2019-8341",
          source_url: "https://nvd.nist.gov/vuln/detail/CVE-2019-8341",
          description: "An issue was discovered in Jinja2 2.10. The from_string function is prone to Server Side Template Injection (SSTI) where it takes the \"source\" parameter as a template object, renders it, and then returns it. The attacker can exploit it with {{INJECTION COMMANDS}} in a URI.",
          base_score: 9.8,
          severity: "CRITICAL"
        }
      ],
      total_findings: 1
    },
    {
      package_name: "pyyaml",
      installed_version: "5.3",
      cpe: "NVD-KEYWORD-MATCH",
      vulnerabilities: [
        {
          id: "CVE-2020-1747",
          source_url: "https://nvd.nist.gov/vuln/detail/CVE-2020-1747",
          description: "A vulnerability was discovered in the PyYAML library in versions before 5.3.1, where it is susceptible to arbitrary code execution when it processes untrusted YAML files through the full_load method or with the FullLoader loader.",
          base_score: 9.8,
          severity: "CRITICAL"
        },
        {
          id: "CVE-2025-50460",
          source_url: "https://nvd.nist.gov/vuln/detail/CVE-2025-50460",
          description: "A remote code execution (RCE) vulnerability exists in the ms-swift project version 3.3.0 due to unsafe deserialization in tests/run.py using yaml.load() from the PyYAML library (versions = 5.3.1).",
          base_score: 9.8,
          severity: "CRITICAL"
        }
      ],
      total_findings: 2
    },
    {
      package_name: "requests",
      installed_version: "2.25.1",
      cpe: "NVD-KEYWORD-MATCH",
      vulnerabilities: [
        {
          id: "CVE-2023-29530",
          source_url: "https://nvd.nist.gov/vuln/detail/CVE-2023-29530",
          description: "Laminas Diactoros provides PSR HTTP Message implementations. Users providing a newline at the start or end of a header key or value can cause an invalid message leading to denial of service vectors.",
          base_score: 7.5,
          severity: "HIGH"
        },
        {
          id: "CVE-2024-36401",
          source_url: "https://nvd.nist.gov/vuln/detail/CVE-2024-36401",
          description: "GeoServer installation due to unsafely evaluating property names as XPath expressions. This allows Remote Code Execution (RCE) by unauthenticated users through specially crafted input.",
          base_score: 9.8,
          severity: "CRITICAL"
        }
      ],
      total_findings: 2
    }
  ]
};