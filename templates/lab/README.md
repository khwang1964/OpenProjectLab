# {{ title }}

Week {{ week }}

## Objectives

{% if objectives %}
{% for objective in objectives %}
- {{ objective }}
{% endfor %}
{% else %}
- Define the learning objectives for this lab.
{% endif %}

## Instructions

{% if instructions %}
{% for instruction in instructions %}
{{ loop.index }}. {{ instruction }}
{% endfor %}
{% else %}
Add the lab instructions here.
{% endif %}

## Expected Outputs

{% if expected_outputs %}
{% for output in expected_outputs %}
- {{ output }}
{% endfor %}
{% else %}
- Document the expected outputs for this lab.
{% endif %}

## Validation

{% if validation_steps %}
{% for step in validation_steps %}
- {{ step }}
{% endfor %}
{% else %}
- Add validation steps for the completed lab.
{% endif %}
