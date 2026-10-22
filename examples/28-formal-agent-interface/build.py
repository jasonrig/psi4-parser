"""Exercise compact CLI planning and measure saved-response sizes without execution."""

import argparse
import json
import sys
from pathlib import Path

from click.testing import CliRunner

from psi4_parser.cli import main as cli
from psi4_parser.formal.interface_models import ProposalSummary


class _Arguments:
    request: Path
    capabilities: Path
    destination: Path


def main() -> None:
    """Save a CLI walkthrough, complete records, bundle, and response-size measures.

    Raises:
        SystemExit: A CLI operation fails or the supplied request has no accepted plan.
    """
    examples = Path(__file__).parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--request",
        type=Path,
        default=(examples / "25-formal-counterpoise-study/saved/request.json"),
    )
    parser.add_argument(
        "--capabilities", type=Path, default=examples / "formal-demo-capabilities.json"
    )
    args = parser.parse_args(namespace=_Arguments())
    args.destination.mkdir()
    common = ["formal", "--workspace", str(args.destination / "workspace")]
    runner = CliRunner()
    responses: list[Path] = []

    def run(name: str, arguments: list[str]) -> str:
        result = runner.invoke(cli, [*common, *arguments])
        path = args.destination / f"{name}.json"
        path.write_text(result.stdout, encoding="utf-8")
        responses.append(path)
        if result.exit_code:
            (args.destination / f"{name}.stderr.txt").write_text(
                result.stderr, encoding="utf-8"
            )
            raise SystemExit(f"CLI returned {result.exit_code}; inspect {path}")
        return result.stdout

    run("01-schema", ["schema", "request", "--definition", "Model", "--field", "basis"])
    run("02-contract", ["contracts", "--driver", "optimize"])
    run(
        "03-capabilities",
        [
            "capabilities",
            str(args.capabilities),
            "--name",
            "scf",
            "--driver",
            "energy",
            "--limit",
            "2",
        ],
    )
    proposal = ProposalSummary.model_validate_json(
        run(
            "04-proposal",
            [
                "propose",
                str(args.request),
                "--capabilities",
                str(args.capabilities),
            ],
        )
    )
    if proposal.plan is None:
        raise SystemExit(f"No accepted plan; inspect {proposal.proposal.path}")
    run(
        "05-assumptions",
        [
            "explain",
            proposal.proposal.handle,
            "--section",
            "assumptions",
            "--limit",
            "2",
        ],
    )
    run(
        "06-export",
        [
            "export",
            proposal.plan.handle,
            "--request",
            str(args.request),
            "--capabilities",
            str(args.capabilities),
            "--destination",
            str(args.destination / "bundle"),
        ],
    )
    measures = {
        "cli_calls": len(responses),
        "response_bytes": {path.name: path.stat().st_size for path in responses},
        "total_response_bytes": sum(path.stat().st_size for path in responses),
        "full_proposal_bytes": Path(proposal.proposal.path).stat().st_size,
        "choice_count": proposal.choice_count,
        "previewed_choices": len(proposal.choices),
        "responses_contain_smt2": any("smt2" in path.read_text() for path in responses),
        "measurement": "UTF-8 bytes, not model token counts or execution performance",
    }
    (args.destination / "measurements.json").write_text(
        json.dumps(measures, indent=2) + "\n", encoding="utf-8"
    )
    sys.stdout.write(
        f"CLI walkthrough and construction artifacts: {args.destination}\n"
    )


if __name__ == "__main__":
    main()
