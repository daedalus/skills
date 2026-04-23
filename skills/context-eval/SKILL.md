---
name: context-eval
description: Evaluate and compare nanocode context management strategies (sliding_window, summary, importance, compaction, topic_id). Use when benchmarking context strategies, measuring token efficiency, comparing compaction quality, or optimizing context usage. Tests all strategies with realistic conversation flows.
---

# Context Strategy Evaluator

Tests and compares nanocode context management strategies via A/B testing.

## When to Use

- User wants to benchmark context strategies
- Comparing token efficiency across strategies
- Evaluating compaction quality (summary vs topic-ID)
- Measuring hallucination rates in long conversations
- Optimizing context limits

## Strategies Tested

1. **sliding_window** - Keep last N messages
2. **summary** - Summarize old messages with LLM
3. **importance** - Keep high-importance messages
4. **compaction** - Full context compaction
5. **topic_id** - Topic ID references (your new strategy)

## Test Methodology

### Step 1: Load nanocode ContextManager

```python
import sys
sys.path.insert(0, "/home/dclavijo/my_code/nanocode")

from nanocode.context import ContextManager, ContextStrategy, TokenCounter
```

### Step 2: Create Test Conversations

Generate realistic conversation flows:
- Short (5 messages)
- Medium (20 messages)
- Long (50+ messages approaching context limit)

Each message should vary in:
- Role (user/assistant/tool)
- Length (short/long)
- Content type (questions, code, file refs, tool results)

### Step 3: Run Each Strategy

For each strategy, run the test conversation and measure:

```python
def evaluate_strategy(strategy, messages, max_tokens=8000):
    manager = ContextManager(
        max_tokens=max_tokens,
        strategy=strategy,
        model="claude-3-5-sonnet"
    )
    manager.set_system_prompt("You are a coding assistant.")

    for msg in messages:
        manager.add_message(msg["role"], msg["content"])

    result = manager.prepare_messages()
    usage = manager.get_token_usage()

    return {
        "output_count": len(result),
        "input_tokens": usage["current_tokens"],
        "output_tokens": usage["max_tokens"],
        "usage_percent": usage["usage_percent"],
        "messages_preserved": len([m for m in result if m.get("role") != "system"]),
    }
```

### Step 4: Run Full Test Suite

Execute all strategies across all conversation lengths:

```bash
python /home/dclavijo/my_code/nanocode/tests/unit/test_context_strategies.py
```

This produces:
- Token usage per strategy
- Message retention rates
- Quality scores (for summary/compaction)

### Step 5: Aggregate Results

Compare metrics:

| Strategy | Short (tokens) | Medium | Long | Retention % |
|----------|--------------|--------|------|-------------|
| sliding_window | X | X | X | X% |
| summary | X | X | X | X% |
| importance | X | X | X | X% |
| compaction | X | X | X | X% |
| topic_id | X | X | X | X% |

## Key Metrics

1. **Token Efficiency**: Input tokens used / max
2. **Retention**: Messages preserved / original
3. **Quality**: Subjective score (0-10) for compacted content
4. **Latency**: Time per prepare_messages() call
5. **Hallucination**: % of facts lost/misrepresented

## Output Format

Save results to `context-eval-results.json`:

```json
{
  "timestamp": "2024-01-01T00:00:00",
  "strategies": ["sliding_window", "summary", "importance", "compaction", "topic_id"],
  "conversations": [
    {
      "length": "short",
      "results": {
        "topic_id": {
          "input_tokens": 500,
          "output_count": 10,
          "retention_pct": 95,
          "quality": 8
        }
      }
    }
  ],
  "recommendation": "topic_id for long conversations"
}
```

## Analysis Guide

### When topic_id wins:
- Long conversations (>30 messages)
- High entity reuse (same files/functions referenced)
- Hallucination prevention critical

### When summary wins:
- Simple conversations
- Fast response needed
- Lower context limits

### When importance wins:
- Mixed content quality
- Some messages more important than others

## Tips

- Use same LLM for all strategies when testing summary/compaction
- Run each test 3x and average for variance
- Test with real conversations from your use cases
- Focus on the metric that matters most for your use case

## Limitations

- Requires actual LLM for summary/compaction tests
- Some strategies may need more tokens for quality
- Results vary by model and conversation type