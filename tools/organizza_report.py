"""Riordina i PDF esistenti senza rigenerare i report.

Eseguire: python -m tools.organizza_report
"""
from gioover25.report_retention import organize_reports


if __name__ == "__main__":
    result = organize_reports()
    print("[REPORT] Archivio riordinato: " +
          ", ".join(f"{key}={value}" for key, value in result.items()))
