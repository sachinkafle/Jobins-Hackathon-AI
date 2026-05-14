# Job Conditions Generator

This utility generates `application_condition` and `welcome_condition` from `pb_job.job_description`.

## Files

- `app/services/job_condition_generator.py`: rules-based parser
- `app/db/populate_job_conditions.py`: runner script (dry-run by default)
- `app/tests/test_job_condition_generator.py`: unit tests

## Run

Dry run (no DB writes):

```bash
cd /Users/binaya/code/hackathon/Jobins-Hackathon-AI
python -m app.db.populate_job_conditions
```

Single job dry run:

```bash
cd /Users/binaya/code/hackathon/Jobins-Hackathon-AI
python -m app.db.populate_job_conditions --job-id 2001
```

Apply updates:

```bash
cd /Users/binaya/code/hackathon/Jobins-Hackathon-AI
python -m app.db.populate_job_conditions --apply
```

## Notes

- Mandatory requirement lines go to `application_condition`.
- Preferred/plus lines go to `welcome_condition`.
- Existing non-empty values are preserved.

