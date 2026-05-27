"""Compliance checklist generation."""

from pathlib import Path
from datetime import datetime

from .models import Work
from .logger import PrivacySafeLogger


class ComplianceChecker:
    """Generates compliance checklists for human review."""

    def __init__(self, logger: PrivacySafeLogger):
        """Initialize compliance checker.

        Args:
            logger: Logger instance
        """
        self.logger = logger

    def generate_checklist(self, work: Work, output_path: Path) -> Path:
        """Generate compliance review checklist.

        Args:
            work: Work instance
            output_path: Output file path

        Returns:
            Path to checklist file
        """
        checklist = self._build_checklist(work)

        with output_path.open('w', encoding='utf-8') as f:
            f.write(checklist)

        self.logger.info(f"Compliance checklist generated: {output_path.name}")

        return output_path

    def _build_checklist(self, work: Work) -> str:
        """Build checklist markdown content.

        Args:
            work: Work instance

        Returns:
            Checklist markdown string
        """
        return f"""# Compliance Review Checklist

**Work ID:** {work.work_id}
**Title:** {work.title}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## General Content Review

### Legal & Rights
- [ ] No real persons depicted without consent or valid license
- [ ] No copyrighted characters (Disney, Marvel, anime characters, etc.)
- [ ] No trademarked content without permission
- [ ] No violation of personality rights or publicity rights

### Age & Representation
- [ ] Age appearance appropriate for intended platform
- [ ] No depiction of minors in inappropriate contexts
- [ ] Character age clearly distinguishable as adult

### Platform Compliance
- [ ] Platform Terms of Service compliance verified
- [ ] Content rating appropriate for distribution channel
- [ ] Platform-specific restrictions reviewed

### Content Categories (if applicable)
- [ ] Violence level within acceptable range
- [ ] Sexual content level within acceptable range
- [ ] Controversial themes handled appropriately

---

## Technical Quality

### Image Quality
- [ ] Image resolution meets minimum requirements
- [ ] No generation artifacts or corruption
- [ ] Consistent style across series
- [ ] Color balance and exposure acceptable

### File Management
- [ ] All files properly numbered and organized
- [ ] File formats compatible with distribution platform
- [ ] File sizes within acceptable range
- [ ] No duplicate or test images included

---

## Distribution Readiness

### Package Contents
- [ ] Sample images selected and separated
- [ ] Sales package contains only approved images
- [ ] Metadata file included and accurate
- [ ] ZIP archive created and tested

### Documentation
- [ ] Work description accurate and appropriate
- [ ] Content warnings added if necessary
- [ ] Attribution requirements met
- [ ] License information included if required

### Final Verification
- [ ] All images reviewed by human reviewer
- [ ] Private/sensitive prompts not exposed in metadata
- [ ] Package tested for extractability
- [ ] Distribution platform requirements verified

---

## Sign-Off

**Reviewer Name:** _______________

**Review Date:** _______________

**Approval Status:** [ ] APPROVED  [ ] REJECTED  [ ] NEEDS REVISION

**Notes:**
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

**IMPORTANT REMINDER:**
This checklist is for general compliance review. Platform-specific requirements
may vary. Always verify the specific requirements of your distribution platform
before final publication.
"""
