"""Test scenarios and evaluation for PC Configuration Agent."""
from langgraph_agent import PCConfigAgentLangGraph
import json


class TestScenarios:
    """Test scenarios for evaluating the agent."""
    
    def __init__(self):
        self.agent = PCConfigAgentLangGraph()
    
    def run_scenario(self, scenario_name: str, user_input: str, expected_outcomes: list) -> dict:
        """Run a single test scenario."""
        print(f"\n{'='*60}")
        print(f"Running Scenario: {scenario_name}")
        print(f"{'='*60}\n")
        
        self.agent.reset()
        
        # Get recommendation
        rec_result = self.agent.invoke(user_input)
        print(f"Requirements: {rec_result['requirements']}")
        print(f"\nRecommendation:\n{rec_result['response']}")
        
        # Get trace
        trace = self.agent.get_trace()
        
        # Evaluate against expected outcomes
        evaluation = self._evaluate_outcome(rec_result['response'], expected_outcomes)
        
        return {
            "scenario": scenario_name,
            "user_input": user_input,
            "requirements": rec_result['requirements'],
            "recommendation": rec_result['response'],
            "trace": trace,
            "evaluation": evaluation
        }
    
    def _evaluate_outcome(self, response: str, expected_outcomes: list) -> dict:
        """Evaluate if response meets expected outcomes."""
        results = []
        response_lower = response.lower()
        
        for outcome in expected_outcomes:
            passed = outcome.lower() in response_lower
            results.append({
                "expected": outcome,
                "passed": passed
            })
        
        return {
            "total_outcomes": len(expected_outcomes),
            "passed": sum(1 for r in results if r["passed"]),
            "details": results
        }
    
    def run_all_scenarios(self):
        """Run all test scenarios."""
        scenarios = [
            {
                "name": "Budget Gaming PC",
                "input": "I need a gaming PC for 1080p gaming with a $1000 budget",
                "expected": [
                    "CPU",
                    "motherboard",
                    "memory",
                    "video card",
                    "power supply",
                    "case",
                    "compatible"
                ]
            },
            {
                "name": "Productivity/Content Creation",
                "input": "I need a PC for video editing and 3D rendering with a $2000 budget",
                "expected": [
                    "CPU",
                    "motherboard",
                    "memory",
                    "video card",
                    "storage",
                    "compatible"
                ]
            },
            {
                "name": "General Use Office PC",
                "input": "I need a basic PC for office work and web browsing with a $500 budget",
                "expected": [
                    "CPU",
                    "motherboard",
                    "memory",
                    "storage",
                    "case",
                    "power supply"
                ]
            },
            {
                "name": "High-End Gaming",
                "input": "I want a high-end gaming PC for 4K gaming with a $3000 budget",
                "expected": [
                    "CPU",
                    "motherboard",
                    "memory",
                    "video card",
                    "power supply",
                    "case",
                    "storage"
                ]
            },
            {
                "name": "Budget Constraint Handling",
                "input": "I need a gaming PC but I only have $400",
                "expected": [
                    "budget",
                    "recommendation",
                    "components"
                ]
            }
        ]
        
        results = []
        for scenario in scenarios:
            result = self.run_scenario(
                scenario["name"],
                scenario["input"],
                scenario["expected"]
            )
            results.append(result)
            
            # Print evaluation summary
            eval_summary = result["evaluation"]
            print(f"\nEvaluation: {eval_summary['passed']}/{eval_summary['total_outcomes']} outcomes passed")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n{'='*60}")
        print("All scenarios completed. Results saved to test_results.json")
        print(f"{'='*60}")
        
        return results


def main():
    """Run evaluation."""
    tester = TestScenarios()
    results = tester.run_all_scenarios()
    
    # Print overall summary
    total_passed = sum(r["evaluation"]["passed"] for r in results)
    total_outcomes = sum(r["evaluation"]["total_outcomes"] for r in results)
    
    print(f"\nOverall: {total_passed}/{total_outcomes} outcomes passed across all scenarios")


if __name__ == "__main__":
    main()
