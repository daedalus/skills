#!/usr/bin/env python3
"""
Automated evaluator for SKILL.md (AlphaEvolve skill file).
Score = 0.0-1.0, higher = better.
Fully automated, runs in <5 seconds.

Includes Time Metric Evaluator pattern: when two solutions are correct, faster wins.
"""

import re
import ast
import sys
from pathlib import Path

def evaluate_skill_md(content: str) -> float:
    """
    Evaluate SKILL.md content.
    Returns score 0.0-1.0 based on objective criteria.
    """
    score = 0.0
    max_score = 0.0
    lines = content.split('\n')
    line_count = len(lines)
    
    # === Criterion 1: Key Sections Present (25 points) ===
    max_score += 25
    required_sections = [
        '## Quick Start',
        '## Core Principle',
        '## When NOT to Use',
        '## Phase0:',
        '## Phase1:',
        '## Phase2:',
        '## Phase3:',
        '## Phase4:',
        '## Phase5:',
        '## Metrics and Tracking',
        '## Troubleshooting',
        '## References',
        '## Checklist Before Starting',
        '## Common Pitfalls',
    ]
    for section in required_sections:
        if section in content:
            score += 25 / len(required_sections)
    
    # === Criterion 2: Code Examples are Valid Python (25 points) ===
    max_score += 25
    code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)
    if code_blocks:
        valid_count = 0
        for block in code_blocks:
            try:
                # Try to parse as Python (not exec, just syntax check)
                ast.parse(block)
                valid_count += 1
            except SyntaxError:
                pass
        score += 25 * (valid_count / len(code_blocks))
    
    # === Criterion 3: New Metrics Covered (20 points) ===
    max_score += 20
    key_metrics = [
        'Relative Progress',
        'PDI',
        'Population Diversity Index',
        'surrogate',
        'Genealogical Diversity',
        'QD Score',
        'Verbalized Sampling',
        'Strategy Evolution',
        'Expected Improvement',
        'Cascaded Evaluation',
    ]
    covered = sum(1 for m in key_metrics if m.lower() in content.lower())
    score += 20 * (covered / len(key_metrics))
    
    # === Criterion 4: Line Count Reasonable (15 points) ===
    max_score += 15
    # Penalize too short (<400) or too long (>800)
    if 400 <= line_count <= 800:
        score += 15
    elif 300 <= line_count < 400 or 800 < line_count <= 900:
        score += 10
    elif line_count >= 200:
        score += 5
    
    # === Criterion 5: References Present (15 points) ===
    max_score += 15
    ref_section = content.split('## References')
    if len(ref_section) > 1:
        # Get everything after ## References, stop at next ## (section header)
        after_ref = ref_section[1]
        # Find next ## section (not ### subsection)
        next_section = after_ref.find('\n## ')
        if next_section >= 0:
            ref_content = after_ref[:next_section]
        else:
            ref_content = after_ref
        # Count lines starting with "- " (reference entries)
        ref_lines = [l for l in ref_content.split('\n') if l.strip().startswith('- ')]
        score += min(15, len(ref_lines) * 1.5)
    
    # Normalize to 0.0-1.0
    return score / max_score if max_score > 0 else 0.0


def evaluate_file(filepath: str) -> float:
    """Evaluate a SKILL.md file."""
    path = Path(filepath)
    if not path.exists():
        return 0.0
    return evaluate_skill_md(path.read_text())


if __name__ == '__main__':
    # Evaluate current SKILL.md
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'SKILL.md'
    score = evaluate_file(filepath)
    print(f"{score:.4f}")
