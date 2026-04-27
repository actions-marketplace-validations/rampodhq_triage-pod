from __future__ import annotations

from jinja2 import Environment, StrictUndefined

from triagepod.domain.models import MissingInfoStatus, TriageResult

COMMENT_MARKER = "<!-- triagepod:v1 -->"

TEMPLATE = """Thanks for opening this issue. TriagePod completed an initial review.

**Assessment**
- Classification: `{{ result.classification.classification.value }}`
  {% if result.classification.confidence -%}
  ({{ result.classification.confidence.value }} confidence)
  {%- endif %}
- Rationale: {{ result.classification.rationale }}
{% if result.duplicates %}

**Possible duplicates**
{% for candidate in result.duplicates -%}
- #{{ candidate.issue_number }}:
  [{{ candidate.title }}]({{ candidate.html_url }})
  - {{ "%.0f"|format(candidate.score * 100) }}% match.
  {{ candidate.rationale }}
{% endfor -%}
{% endif %}
{% if result.missing_info.status.value == "incomplete" %}

**Details requested**
{% for field in result.missing_info.missing_fields -%}
- {{ field.prompt }}
{% endfor -%}
{% for note in result.missing_info.rationale -%}
- {{ note }}
{% endfor -%}
{% endif %}
{% if result.label_suggestions %}

**Label suggestions**
{% for suggestion in result.label_suggestions -%}
- `{{ suggestion.label }}`: {{ suggestion.reason }}
{% endfor -%}
{% endif %}
{% if result.routing.should_route %}

**Suggested route**
This may fit better in GitHub Discussions{% if result.routing.category %}
under `{{ result.routing.category }}`{% endif %}. {{ result.routing.reason }}
{% endif %}

**Next step**
{% if result.missing_info.status.value == "incomplete" -%}
Please add the requested details so maintainers can investigate efficiently.
{% elif result.duplicates -%}
Please review the possible duplicate issues before maintainers continue triage.
{% else -%}
This issue appears ready for maintainer review.
{% endif %}
"""


class ProfessionalCommentRenderer:
    def __init__(self) -> None:
        self.environment = Environment(
            undefined=StrictUndefined,
            autoescape=True,
            trim_blocks=True,
        )
        self.template = self.environment.from_string(TEMPLATE)

    def render(self, result: TriageResult) -> str:
        body = self.template.render(
            result=result,
            MissingInfoStatus=MissingInfoStatus,
        ).strip()
        return f"{COMMENT_MARKER}\n{body}"
