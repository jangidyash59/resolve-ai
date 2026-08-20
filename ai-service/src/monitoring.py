"""
Monitoring utilities for circuit breaker and resolution metrics.
Use this to track escalation rates, similarity distributions, and performance.
"""
import json
import logging
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CircuitBreakerMetrics:
    """
    Tracks circuit breaker performance metrics for monitoring and calibration.
    """
    
    def __init__(self, log_file: Optional[Path] = None):
        self.metrics = defaultdict(list)
        self.log_file = log_file or Path("circuit_breaker_metrics.jsonl")
        
    def record_ticket(
        self,
        ticket_id: str,
        query: str,
        top_similarity: float,
        threshold: float,
        action: str,  # "resolved" or "escalated"
        latency_ms: float,
        token_usage: Optional[int] = None
    ):
        """Record a ticket processing event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "ticket_id": ticket_id,
            "query_preview": query[:100],
            "top_similarity": round(top_similarity, 3),
            "threshold": threshold,
            "action": action,
            "latency_ms": round(latency_ms, 2),
            "token_usage": token_usage,
            "passed_threshold": top_similarity >= threshold
        }
        
        # Store in memory
        self.metrics["events"].append(event)
        
        # Append to log file
        if self.log_file:
            try:
                with open(self.log_file, "a") as f:
                    f.write(json.dumps(event) + "\n")
            except Exception as e:
                logger.error(f"Failed to write metrics: {e}")
    
    def get_summary(self) -> Dict:
        """Generate summary statistics."""
        events = self.metrics["events"]
        
        if not events:
            return {"error": "No events recorded"}
        
        total = len(events)
        escalated = sum(1 for e in events if e["action"] == "escalated")
        resolved = total - escalated
        
        similarities = [e["top_similarity"] for e in events]
        latencies = [e["latency_ms"] for e in events]
        
        escalated_latencies = [e["latency_ms"] for e in events if e["action"] == "escalated"]
        resolved_latencies = [e["latency_ms"] for e in events if e["action"] == "resolved"]
        
        tokens_used = [e["token_usage"] for e in events if e["token_usage"] is not None]
        
        return {
            "total_tickets": total,
            "escalated": escalated,
            "resolved": resolved,
            "escalation_rate": round(escalated / total * 100, 2) if total > 0 else 0,
            "similarity_stats": {
                "min": round(min(similarities), 3),
                "max": round(max(similarities), 3),
                "mean": round(sum(similarities) / len(similarities), 3),
                "median": round(sorted(similarities)[len(similarities) // 2], 3)
            },
            "latency_stats": {
                "overall_mean_ms": round(sum(latencies) / len(latencies), 2),
                "escalated_mean_ms": round(sum(escalated_latencies) / len(escalated_latencies), 2) if escalated_latencies else 0,
                "resolved_mean_ms": round(sum(resolved_latencies) / len(resolved_latencies), 2) if resolved_latencies else 0,
                "speedup_factor": round(
                    (sum(resolved_latencies) / len(resolved_latencies)) / (sum(escalated_latencies) / len(escalated_latencies)),
                    2
                ) if escalated_latencies and resolved_latencies else 0
            },
            "token_usage": {
                "total_tokens": sum(tokens_used) if tokens_used else 0,
                "avg_per_resolved_ticket": round(sum(tokens_used) / resolved, 2) if resolved and tokens_used else 0,
                "tokens_saved_by_escalation": escalated * (sum(tokens_used) / resolved if resolved and tokens_used else 0)
            }
        }
    
    def print_summary(self):
        """Print formatted summary to console."""
        summary = self.get_summary()
        
        if "error" in summary:
            print(f"\n❌ {summary['error']}")
            return
        
        print("\n" + "=" * 80)
        print("  Circuit Breaker Performance Summary")
        print("=" * 80)
        
        print(f"\n📊 Overall Metrics:")
        print(f"   Total Tickets:     {summary['total_tickets']}")
        print(f"   Resolved:          {summary['resolved']} ({100 - summary['escalation_rate']:.1f}%)")
        print(f"   Escalated:         {summary['escalated']} ({summary['escalation_rate']:.1f}%)")
        
        print(f"\n🎯 Similarity Distribution:")
        stats = summary['similarity_stats']
        print(f"   Min:    {stats['min']:.3f}")
        print(f"   Mean:   {stats['mean']:.3f}")
        print(f"   Median: {stats['median']:.3f}")
        print(f"   Max:    {stats['max']:.3f}")
        
        print(f"\n⚡ Latency Performance:")
        lat = summary['latency_stats']
        print(f"   Overall Mean:    {lat['overall_mean_ms']:.2f}ms")
        print(f"   Escalated Mean:  {lat['escalated_mean_ms']:.2f}ms  (circuit breaker bypass)")
        print(f"   Resolved Mean:   {lat['resolved_mean_ms']:.2f}ms  (full LLM pipeline)")
        if lat['speedup_factor'] > 0:
            print(f"   Speedup Factor:  {lat['speedup_factor']:.1f}x faster for escalations")
        
        print(f"\n💰 Token Usage:")
        tok = summary['token_usage']
        print(f"   Total Tokens Used:       {tok['total_tokens']:,}")
        print(f"   Avg per Resolved Ticket: {tok['avg_per_resolved_ticket']:.0f}")
        print(f"   Tokens Saved by Circuit Breaker: ~{tok['tokens_saved_by_escalation']:.0f}")
        
        print("\n" + "=" * 80)
        print("\n💡 Calibration Recommendations:")
        
        if summary['escalation_rate'] > 25:
            print("   ⚠️  High escalation rate (>25%) - consider LOWERING threshold")
        elif summary['escalation_rate'] < 5:
            print("   ⚠️  Low escalation rate (<5%) - verify no hallucinations, consider RAISING threshold")
        else:
            print("   ✅ Escalation rate within acceptable range (5-25%)")
        
        if stats['mean'] < 0.6:
            print("   ⚠️  Low mean similarity - queries may be outside knowledge base coverage")
        
        print()


def analyze_metrics_file(file_path: Path):
    """Analyze metrics from a JSONL log file."""
    metrics = CircuitBreakerMetrics(log_file=None)
    
    try:
        with open(file_path, "r") as f:
            for line in f:
                event = json.loads(line.strip())
                metrics.metrics["events"].append(event)
        
        metrics.print_summary()
        
    except FileNotFoundError:
        print(f"❌ Metrics file not found: {file_path}")
    except Exception as e:
        print(f"❌ Error analyzing metrics: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Analyze specific file
        analyze_metrics_file(Path(sys.argv[1]))
    else:
        # Analyze default file
        analyze_metrics_file(Path("circuit_breaker_metrics.jsonl"))
