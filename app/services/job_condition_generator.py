import re
from typing import List, Tuple


PREFERRED_MARKERS = (
	"preferred",
	"plus",
	"nice to have",
	"bonus",
	"welcome",
	"would be great",
)


def _clean_line(raw: str) -> str:
	line = raw.strip()
	line = re.sub(r"^(?:[\-\*\u2022]|\d+[\.)])\s*", "", line).strip()
	return line


def _split_lines(text: str) -> List[str]:
	return [line for line in (_clean_line(x) for x in text.splitlines()) if line]


def _extract_requirements_section(text: str) -> List[str]:
	lower = text.lower()
	start_tokens = ("requirements:", "qualifications:", "must have:")
	end_tokens = ("responsibilities:", "benefits:", "selection flow:")

	start_idx = -1
	for token in start_tokens:
		idx = lower.find(token)
		if idx != -1:
			start_idx = idx + len(token)
			break

	if start_idx == -1:
		return _split_lines(text)

	end_idx = len(text)
	tail = lower[start_idx:]
	for token in end_tokens:
		idx = tail.find(token)
		if idx != -1:
			end_idx = start_idx + idx
			break

	return _split_lines(text[start_idx:end_idx])


def generate_conditions(job_description: str) -> Tuple[str, str]:
	if not job_description or not job_description.strip():
		return "", ""

	lines = _extract_requirements_section(job_description)
	mandatory: List[str] = []
	welcome: List[str] = []

	for line in lines:
		normalized = line.lower()
		if any(marker in normalized for marker in PREFERRED_MARKERS):
			welcome.append(line)
		else:
			mandatory.append(line)

	if not mandatory and lines:
		mandatory = lines[: min(8, len(lines))]

	if not welcome:
		welcome = [
			"Relevant certification is preferred.",
			"Experience in a similar domain is a plus.",
		]

	application_condition = "\n".join(f"- {x}" for x in mandatory[:10])
	welcome_condition = "\n".join(f"- {x}" for x in welcome[:6])
	return application_condition, welcome_condition

